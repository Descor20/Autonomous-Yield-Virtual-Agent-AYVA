import pyttsx3
from src.speaker.piper import parler_piper

def parler_systeme(phrase: str, voice_id: str):
    moteur = pyttsx3.init()
    moteur.setProperty("voice", voice_id)
    moteur.say(phrase)
    moteur.runAndWait()


def speak(phrase: str, voix: dict):
    if voix["type"] == "piper":
        parler_piper(phrase, voix)
    else:
        parler_systeme(phrase, voix["id"])