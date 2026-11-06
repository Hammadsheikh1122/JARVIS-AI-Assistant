import requests
import pyttsx3


def speak(text):
    print("\nJARVIS:", text)

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Voice Error:", e)


def ask_ai(question):

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "qwen2.5:1.5b",

        "prompt": (
            "You are Jarvis, a helpful personal AI assistant. "
            "Answer in simple English. "
            "Keep every answer within 2 short sentences. "
            "Do not give long explanations. "
            "Question: " + question
        ),

        "stream": False,

        "options": {
            "num_predict": 50,
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
        print("JARVIS: Ollama is not running.")

    except Exception as e:
        print("Error:", e)


print("================================")
print("       JARVIS AI ASSISTANT")
print("================================")

speak("Hello sir. Jarvis is ready.")

while True:

    question = input("\nYOU: ").strip()

    if question.lower() in ["exit", "quit", "bye"]:
        speak("Goodbye sir.")
        break

    if not question:
        continue

    ask_ai(question)