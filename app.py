
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please type a message."})

        prompt = f"""
You are JARVIS, a smart personal AI assistant.

Understand the user's language.
Reply in the same language.
If the user writes Roman Urdu, reply in Roman Urdu.
If the user writes English, reply in English.
Keep answers clear and concise.

User: {user_message}
JARVIS:
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 150,
                    "temperature": 0.7
                }
            },
            timeout=120
        )

        response.raise_for_status()

        answer = response.json()["response"].strip()

        return jsonify({"reply": answer})

    except requests.exceptions.ConnectionError:
        return jsonify({
            "reply": "Sir, Ollama is not running. Please start Ollama."
        }), 503

    except Exception as error:
        print("ERROR:", error)
        return jsonify({
            "reply": "Sorry sir, something went wrong."
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
