import speech_recognition as sr

def get_microphone(display=False) :
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with microphone as source:
        if (display) :
            print("Ajustement au bruit ambiant...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
    return (recognizer, microphone)

def listen(microphone, recognizer, display=False):
    audio = None
    with microphone as source:
        audio = recognizer.listen(source)
    return audio