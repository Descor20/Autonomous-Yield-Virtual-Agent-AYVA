from .spanlib import SPANS
import json

def set_parent(child_id: str, parent_id: str, trace_id = None, display: bool = False) :
    for s in SPANS :
        if (display) :
            print("---> Update trace parent:", s)
        s["trace_id"] = trace_id
        if (s["trace_id"] == child_id) :
            if (s["parent_id"] == None) :
                s["parent_id"] = parent_id
                if (display) :
                    print("  ---> Corrected to", parent_id) 

def afficher_trace(trace_id: str, largeur: int = 36) -> None:
    spans = sorted((s for s in SPANS if s["trace_id"] == trace_id), key=lambda s: s["debut"])
    t0, t1 = spans[0]["debut"], max(s["fin"] for s in spans)
    duree = (t1 - t0) or 1e-9
    profondeur = {}
    for s in spans:
        profondeur[s["id"]] = 0 if s["parent_id"] is None else profondeur.get(s["parent_id"], 0) + 1
        a = int((s["debut"] - t0) / duree * largeur)
        b = max(a + 1, int((s["fin"] - t0) / duree * largeur))
        at, info = s["attributs"], ""
        if s["type"] == "llm":
            info = f"{at.get('tokens_entree')} → {at.get('tokens_sortie')} tok · {at.get('stop', '')}"
        elif s["type"] == "tool":
            info = json.dumps(at.get("entree"), ensure_ascii=False)[:70]
            if at.get("erreur_outil"):
                info += "  ⚠ " + at["erreur_outil"][:60]
        nom = "  " * profondeur[s["id"]] + s["nom"]
        print(f"{nom[:40]:<40} |{' ' * a}{'█' * (b - a)}{' ' * (largeur - b)}| {s['fin'] - s['debut']:5.2f} s  {info}")