from ..base import Agent

class Agent_Id(Agent) :
    """
    Ceci est un agent de recherche dans les bases de donnée interne du système. Il a accès a plusieurs bases de données tel que les identitée des personnes qui utilisent ton service.
    """
    def __init__(self, nom, system, outils = [], max_etapes = 8, version = "v1", garde=None, filtre_resultat=None, filtre_sortie=None):
        super().__init__(nom, system, outils, max_etapes, version, garde, filtre_resultat, filtre_sortie)
