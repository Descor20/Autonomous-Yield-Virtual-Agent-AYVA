from ..base import Agent

class Agent_Web(Agent) :
    """
    Ceci est un agent de recherche web. Il a accès a plusieurs fonction d'appel d'API tel que la recherche de la météo.
    """
    def __init__(self, nom, system, outils = [], max_etapes = 8, version = "v1", garde=None, filtre_resultat=None, filtre_sortie=None):
        super().__init__(nom, system, outils, max_etapes, version, garde, filtre_resultat, filtre_sortie)
