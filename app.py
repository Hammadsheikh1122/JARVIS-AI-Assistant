
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please type a message."})

        if not GEMINI_API_KEY:
            return jsonify({
                "reply": "Sir, Gemini API key is missing. Please check Render settings."
            }), 500

        prompt = f"""
You are JARVIS, a smart personal AI assistant.

Understand the user's language.
Reply in the same language.
If the user writes Roman Urdu, reply in Roman Urdu.
If the user writes English, reply in English.
Keep answers clear, helpful and concise.

User: {user_message}
JARVIS:
"""

        response = requests.post(
            GEMINI_URL,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 300
                }
            },
            timeout=60
        )

        if response.status_code != 200:
            print("GEMINI ERROR:", response.status_code, response.text)

            return jsonify({
                "reply": "Sir, Gemini AI is temporarily unavailable. Please try again."
            }), 502

        result = response.json()

        answer = (
            result["candidates"][0]["content"]["parts"][0]["text"].strip()
        )

        return jsonify({"reply": answer})

    except requests.exceptions.Timeout:
        return jsonify({
            "reply": "Sir, the AI is taking too long. Please try again."
        }), 504

    except Exception as error:
        print("ERROR:", error)
        return jsonify({
            "reply": "Sorry sir, something went wrong."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
    )
