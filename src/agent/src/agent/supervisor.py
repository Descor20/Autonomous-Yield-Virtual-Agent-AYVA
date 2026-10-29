import asyncio

from concurrent.futures import ThreadPoolExecutor

from .base          import *
from src.tools      import new_tool
from src.trace.base import set_parent


# -------- Utils function -------- #
global TRACE
global WORKERS
TRACE = []
WORKERS = {}

def AddWorkers(workers, display=False) :
    global WORKERS
    for worker in workers.keys() :
        if (display) :
            print(f"Adding worker: {worker}")
        if not (worker in WORKERS.keys()) :
            WORKERS[worker] = workers[worker]

def GetWorkers() :
    global WORKERS
    return WORKERS

def GetTrace() :
    global TRACE
    return TRACE

def SetTrace(value: list, display = False) :
    global TRACE
    if (display) :
        print("--> setTrace:", value)
    TRACE = value


def deleguer(worker: str, consigne: str, display: bool = False) -> Run:
    """
    Appelle les sous agents spécifiques pour leurs donner une tache.
    """
    WORKERS = GetWorkers()
    SetTrace(["loading..."])

    async def inner_deleguer(worker: str, consigne: str) -> Run:
        print(f"launching worker: {worker} on task \"{consigne}\"")
        try :
            if (not worker in list(WORKERS.keys())) :
                raise ValueError("Le worker n'existe pas")
            resultat = await execute(WORKERS[worker], consigne, max_token=8192)
            if (display) :
                print("resultat:", resultat)
            return resultat
        except Exception as e :
            print(type(e), ":", e)
            return {"response": "service unavailable"}
        
    with ThreadPoolExecutor(max_workers=1) as ex:
        result: Run = ex.submit(asyncio.run, inner_deleguer(worker=worker, consigne=consigne)).result()
        SetTrace([result])
        return result.reponse

class Supervisor(Agent) :
    def __init__(self, name, system, agents: dict = {}, max_steps = 8, version = "v1", garde=None, result_filter=None, output_filter=None):
        self.worker_description = "Confie une sous-tâche à un worker et renvoie son résultat. Le worker ne voit QUE ta consigne : " \
            "elle doit contenir toutes les informations nécessaires.\n"
        AddWorkers(agents)
        for name in agents.keys() :
            self.worker_description += "worker : " + str(name) + " : " + agents[name].__doc__ + "\n"

        tool = new_tool(deleguer, f"Appelle les sous agents spécifiques. {len(agents)} agents sont disponible selon la description suivante :\n{self.worker_description}",
            {
                "worker": {"type": "string", "enum": list(WORKERS), "description": "L'agent à appeler."},
                "consigne": {"type": "string", "description": "La demande le plus précis possible aux autres agents."}
            }, []
        )

        super().__init__(name, system, [tool], max_steps, version, garde, result_filter, output_filter)

    async def run(self, question: str, max_tokens: int = 1024, display: bool = False, USER: str = "Kylian", TODAY : str = "29/10/2026") -> Run:
            _, connection = get_model()
            
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
                            for trace in GetTrace() :
                                if (display) :
                                    print("Trace:", trace)
                                set_parent(trace.trace_id, s_agent["id"], trace_id = s_agent["trace_id"])
                        except Exception as e :
                            if (display) :
                                print("=" * 50 + "\nerror:", e, "\n" + "=" * 50)
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