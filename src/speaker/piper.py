import sys
import os
import io
import pyaudio
import wave
import subprocess
from piper import PiperVoice
from src.speaker.constants import VOICES
import time

def telecharger_voix_piper(nom: str):
    """
    Télécharge une voix Piper via le module officiel, si elle n'est pas
    déjà présente dans le dossier courant.
    """
    print(f"Téléchargement de la voix '{nom}'...")
    subprocess.run(
        [sys.executable, "-m", "piper.download_voices", nom],
        check=True,
    )
    time.sleep(1)
    subprocess.run(
            ["mv", f"{nom}.onnx", f"{VOICES}"],
            check=True,
        )
    time.sleep(0.01)
    subprocess.run(
                ["mv", f"{nom}.onnx.json", f"{VOICES}"],
                check=True,
            )


def parler_piper(phrase: str, voix: dict):
    if voix["a_telecharger"] or not os.path.exists(voix["chemin"]):
        telecharger_voix_piper(voix["nom"])

    voice = PiperVoice.load(voix["chemin"])
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        voice.synthesize_wav(phrase, wav_file)
    buffer.seek(0)
    jouer_wav(buffer)

def jouer_wav(buffer: io.BytesIO):
    with wave.open(buffer, "rb") as wf:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()