import asyncio
import joblib
import json
import sqlite3
import time

from dataclasses        import dataclass, field

from src.trace          import span

global model
global connection
connection = ...
model = ...

def set_model(value, conn) :
    global model
    global connection
    connection = conn
    model = value

def get_model() :
    global model
    global connection
    return model, connection


@dataclass
class Run:
    question: str
    version: str = ""
    reponse: str = ""
    appels_outils: list = field(default_factory=list)   # {"nom", "entree", "sortie", "erreur"}
    trace_id: str = ""
    appels_llm: int = 0
    tokens_entree: int = 0
    tokens_sortie: int = 0
    latence_s: float = 0.0
    arret: str = ""                                     # "fin" ou "max_etapes"

RUNS: dict[str, Run] = {}          # trace_id -> Run, pour retrouver un run à partir de sa trace


class Agent:
    def __init__(self, nom: str, system: str, outils: list[dict] = [],
                 max_etapes: int = 8, version: str = "v1",
                 garde=None, filtre_resultat=None, filtre_sortie=None):
        global model
        self.nom, self.system, self.outils, self.model = nom, system, outils, model
        self.max_etapes, self.version = max_etapes, version
        self.garde, self.filtre_resultat, self.filtre_sortie = garde, filtre_resultat, filtre_sortie

    async def _executer(self, bloc, run: Run, ctx: dict) -> dict:
        outil = next((o for o in self.outils if o["schema"]["name"] == bloc.name), None)
        appel = {"nom": bloc.name, "entree": bloc.input, "sortie": None, "erreur": None}
        run.appels_outils.append(appel)
        with span(f"execute_tool {bloc.name}", type="tool", entree=bloc.input) as s:
            try:
                if outil is None:
                    raise ValueError(f"Outil inconnu : {bloc.name}")
                ctx["nb_outils"] += 1
                if self.garde:
                    self.garde(outil, bloc.input, ctx)            # lève une exception pour bloquer
                res = outil["fonction"](**bloc.input)
                texte = res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
                if outil["non_fiable"]:
                    ctx["contamine"] = True
                if self.filtre_resultat:
                    texte = self.filtre_resultat(bloc.name, texte)
                appel["sortie"] = s["attributs"]["sortie"] = texte
                return {"type": "tool_result", "tool_use_id": bloc.id, "content": texte}
            except Exception as e:
                appel["erreur"] = s["attributs"]["erreur_outil"] = f"{type(e).__name__}: {e}"
                return {"type": "tool_result", "tool_use_id": bloc.id, "content": f"Erreur : {e}", "is_error": True}

    async def run(self, question: str, max_tokens: int = 1024, display: bool = False, USER: str = "Kylian", TODAY : str = "29/10/2026") -> Run:
        global connection
        run = Run(question=question, version=self.version)
        ctx = {"utilisateur": USER, "contamine": False, "nb_outils": 0}
        system = self.system.format(aujourd_hui=TODAY, utilisateur=ctx["utilisateur"])
        tools = [o["schema"] for o in self.outils]
        t0 = time.perf_counter()
        with span(f"invoke_agent {self.nom}", type="agent", entree=question,
                  version=self.version, utilisateur=ctx["utilisateur"]) as s_agent:
            run.trace_id = s_agent["trace_id"]
            messages = [{"role": "user", "content": question}]
            for _ in range(self.max_etapes):
                with span(f"chat {self.model}", type="llm", modele=self.model) as s_llm:
                    try :
                        rep = await connection.messages.create(model=self.model, max_tokens=max_tokens, 
                                                               system=system, tools=tools, messages=messages)
                    except Exception as e :
                        print(e)
                        raise e
                    s_llm["attributs"].update(tokens_entree=rep.usage.input_tokens,
                                              tokens_sortie=rep.usage.output_tokens, stop=rep.stop_reason)
                run.appels_llm += 1
                run.tokens_entree += rep.usage.input_tokens
                run.tokens_sortie += rep.usage.output_tokens
                messages.append({"role": "assistant", "content": rep.content})
                if rep.stop_reason != "tool_use":
                    run.reponse, run.arret = "".join(b.text for b in rep.content if b.type == "text"), "fin"
                    break
                appels = [b for b in rep.content if b.type == "tool_use"]
                resultats = await asyncio.gather(*(self._executer(b, run, ctx) for b in appels))
                messages.append({"role": "user", "content": list(resultats)})
            else:
                run.arret = "max_etapes"
            if self.filtre_sortie:
                run.reponse = self.filtre_sortie(run.reponse)
            s_agent["attributs"].update(sortie=run.reponse, contamine=ctx["contamine"])
        run.latence_s = round(time.perf_counter() - t0, 2)
        return run

    def save(self, filepath: str) -> None:
        "Savegarde l'agent actuel selon un chemin donné."
        joblib.dump(self, filename=filepath)

def load_Agent(filepath: str) -> Agent:
    "Charge un agent depuis un fichier."
    return joblib.load(filepath)



async def execute(agent: Agent, question: str, max_token: int = 2048, display: bool = False, USER: str = "Kylian", TODAY : str = "29/10/2026") -> Run:
    "Lance l'agent dans une base campus neuve (ou celle fournie) : chaque run est isolé."
    run = await agent.run(question, max_tokens=max_token, display=display, USER=USER, TODAY=TODAY)
    RUNS[run.trace_id] = run
    if (display) :
        print("Sub agent return: ", run)
    return run