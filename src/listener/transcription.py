import speech_recognition as sr
import io
from faster_whisper import WhisperModel
from src.listener.constants import TAILLE_MODELE

model = WhisperModel(TAILLE_MODELE, device="cpu", compute_type="int8")
def transcript(behaviour, audio: sr.AudioData, text_id, next_text_id):
    """
    Transcrit l'audio localement avec Whisper et affiche le résultat.
    Tourne dans un thread séparé pour ne pas bloquer l'écoute.
    """
    wav_data = io.BytesIO(audio.get_wav_data())
    segments, _info = model.transcribe(wav_data, language="fr")

    texte = "".join(segment.text for segment in segments).strip()
    return behaviour(texte, text_id, next_text_id)