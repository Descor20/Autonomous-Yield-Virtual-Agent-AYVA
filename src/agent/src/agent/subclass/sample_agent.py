from ..base import Agent

class Agent_Sample(Agent) :
    """
    Ceci est un agent d'exemple, tu ne dois jamais l'appeler quelques soit la tache.
    """
    def __init__(self, nom, system, outils = [], max_etapes = 8, version = "v1", garde=None, filtre_resultat=None, filtre_sortie=None):
        super().__init__(nom, system, outils, max_etapes, version, garde, filtre_resultat, filtre_sortie)
