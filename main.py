
import sounddevice as sd
import speech_recognition as sr
import requests
import pyttsx3


SAMPLE_RATE = 16000
RECORD_SECONDS = 7


def speak(text, language="en"):
    print("\nJARVIS:", text)

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)

        # Windows voices
        voices = engine.getProperty("voices")

        # Select a matching voice when available
        if language == "en":
            for voice in voices:
                if "david" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break

        elif language == "ur":
            print("Note: Urdu voice may not be installed.")

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Voice Error:", e)


def listen():
    print("\nListening... Speak now!")

    try:
        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio = sr.AudioData(
            recording.tobytes(),
            SAMPLE_RATE,
            2
        )

        recognizer = sr.Recognizer()

        print("Understanding your voice...")

        # Google recognition supports multiple language choices.
        # English is the default; Roman Urdu words may be recognized
        # more accurately with an Urdu-capable speech service.
        question = recognizer.recognize_google(
            audio,
            language="en-US"
        )

        print("YOU:", question)
        return question.strip()

    except sr.UnknownValueError:
        print("I could not understand. Please try again.")
        return ""

    except sr.RequestError:
        print("Speech recognition internet error.")
        return ""

    except Exception as e:
        print("Microphone Error:", e)
        return ""


def ask_ai(question):

    url = "http://localhost:11434/api/generate"

    prompt = f"""
You are JARVIS, a multilingual personal AI assistant.

Understand the user's question and identify its language.

Rules:
1. Reply in the same language as the user.
2. Support English, Urdu, Roman Urdu, Hindi, Arabic,
   and other languages.
3. If the user writes or speaks Roman Urdu, reply in Roman Urdu.
4. If the user uses English, reply in English.
5. If the user uses Urdu script, reply in Urdu script.
6. Keep answers short, natural and easy to understand.
7. Never claim you can perform an action unless you can.

User question: {question}
"""

    data = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 100,
            "num_ctx": 2048,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(
            url,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        answer = response.json()["response"].strip()

        speak(answer)

    except requests.exceptions.ConnectionError:
        speak("Sir, Ollama is not running.")

    except Exception as e:
        print("AI Error:", e)
        speak("Sorry sir, something went wrong.")


def main():

    speak("Hello sir. I am Jarvis. How can I help you?")

    while True:

        question = listen()

        if not question:
            continue

        if question.lower() in ["exit", "quit", "goodbye"]:
            speak("Goodbye sir. See you again.")
            break

        ask_ai(question)


if __name__ == "__main__":
    main()
