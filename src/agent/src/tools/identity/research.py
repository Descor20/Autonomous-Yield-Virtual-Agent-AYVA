from difflib import SequenceMatcher

from .base import list_id

def get_id(id: int) -> list[dict] :
    "Recherche un utilisateur par son identifiant unique."
    try :
        ids = list_id()
        for x in ids :
            if (id in x["id"]) :
                return x
        raise ValueError("L'utilisateur recherché n'existe pas.")
    except Exception as e :
            print(f"<find_file>: Exception: {e}")
            raise e

def get_firstname(firstname: str) -> list[dict] :
    "Recherche un utilisateur par similaritée avec un prénom."
    best = 0
    try :
        ids = list_id()
        best = 0
        score = SequenceMatcher(None, firstname, ids[best]["firstname"]).ratio()
        for i in range(len(ids)) :
            tmp = SequenceMatcher(None, firstname, ids[best]["firstname"]).ratio()
            if (tmp > score) :
                score = tmp
                best = i
        if (score <= 0.7) :
            raise ValueError("L'utilisateur recherché n'existe pas.")
        else :
             return ids[best]
    except Exception as e :
            print(f"<find_file>: Exception: {e}")
            raise e

def get_lastname(lastname: str) -> list[dict] :
    "Recherche un utilisateur par similaritée avec un nom de famille."
    best = 0
    try :
        ids = list_id()
        best = 0
        score = SequenceMatcher(None, lastname, ids[best]["lastname"]).ratio()
        for i in range(len(ids)) :
            tmp = SequenceMatcher(None, lastname, ids[best]["lastname"]).ratio()
            if (tmp > score) :
                score = tmp
                best = i
        if (score <= 0.7) :
            raise ValueError("L'utilisateur recherché n'existe pas.")
        else :
             return ids[best]
    except Exception as e :
            print(f"<find_file>: Exception: {e}")
            raise e
