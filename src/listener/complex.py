from src.listener.base import get_microphone, listen
from src.listener.transcription import transcript
import threading
import uuid

def continuous(transcript_behaviour, text_id, display=False):
    recognizer, microphone = get_microphone(display)

    if (display):
        print("🎙️  Écoute en continu démarrée (transcription locale). Ctrl+C pour arrêter.\n")

    try:
        while True:
            audio = listen(microphone, recognizer, display=display)

            if (display):
                print("do not talk")
            next_text_id = uuid.uuid4()
            thread = threading.Thread(target=transcript, args=(transcript_behaviour, audio, text_id, next_text_id))
            thread.start()
            text_id = next_text_id
            if (display):
                print("talk")

    except KeyboardInterrupt:
        if (display) :
            print("\nArrêt de l'écoute.")