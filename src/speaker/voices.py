import glob
import pyttsx3
import sys
from src.speaker.constants import AVAILABLE, VOICES

def lister_voix_piper(dossier: str = "."):
    """
    Combine :
      - les voix Piper déjà présentes (.onnx trouvés dans le dossier)
      - les voix recommandées non encore téléchargées (marquées comme telles)
    """
    voix = []
    noms_deja_presents = set()

    for chemin in sorted(glob.glob(f"{dossier}/*.onnx")):
        nom = chemin.replace("\\", "/").split("/")[-1].removesuffix(".onnx")
        voix.append({"type": "piper", "nom": nom, "chemin": chemin, "a_telecharger": False})
        noms_deja_presents.add(nom)

    for nom in AVAILABLE:
        if nom not in noms_deja_presents:
            voix.append({"type": "piper", "nom": nom, "chemin": f"{nom}.onnx", "a_telecharger": True})

    return voix

def lister_voix_systeme():
    """
    Récupère les voix installées sur le système via pyttsx3.
    """
    moteur = pyttsx3.init()
    voix = []
    for v in moteur.getProperty("voices"):
        voix.append({"type": "systeme", "nom": v.name, "id": v.id})
    moteur.stop()
    return voix


def choisir_voix(indiex=None) -> dict:
    """
    Affiche la liste combinée (Piper + système) et demande à l'utilisateur
    de choisir une voix. Retourne le dict de la voix choisie.
    """
    voix_piper = lister_voix_piper(dossier=VOICES)
    voix_systeme = lister_voix_systeme()
    toutes_les_voix = voix_piper + voix_systeme

    if not toutes_les_voix:
        print("Aucune voix trouvée (ni Piper, ni système).")
        sys.exit(1)

    print("Voix disponibles :\n")
    for i, v in enumerate(toutes_les_voix):
        if v["type"] == "piper":
            suffixe = " (à télécharger)" if v["a_telecharger"] else ""
            print(f"  [{i}] (Piper) {v['nom']}{suffixe}")
        else:
            print(f"  [{i}] (Système) {v['nom']}")

    if (indiex == None) :
        while True:
            choix = input("\nChoisissez une voix (numéro) : ").strip()
            if choix.isdigit() and 0 <= int(choix) < len(toutes_les_voix):
                return toutes_les_voix[int(choix)]
            print("Choix invalide, réessayez.")
    else :
        return toutes_les_voix[int(indiex)]