
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


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
                "reply": "Sir, Gemini API key is missing."
            }), 500

        response = requests.post(
            GEMINI_URL,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY
            },
            json={
                "model": "gemini-3.8-flash",
                "input": user_message,
                "system_instruction": """
You are JARVIS, a smart personal AI assistant.

Understand the user's language.
Reply in the same language.
If the user writes Roman Urdu, reply in Roman Urdu.
If the user writes English, reply in English.

Be helpful, intelligent and conversational.
Keep answers clear and concise.
""",
                "generation_config": {
                    "temperature": 0.7,
                    "max_output_tokens": 500
                }
            },
            timeout=60
        )

        if response.status_code != 200:
            print("GEMINI ERROR:", response.status_code, response.text)

            return jsonify({
                "reply": "Sir, Gemini AI returned an error. Please try again."
            }), 502

        result = response.json()

        answer = ""

        for step in result.get("steps", []):
            if step.get("type") == "model_output":
                for part in step.get("content", []):
                    if part.get("type") == "text":
                        answer += part.get("text", "")

        if not answer.strip():
            print("GEMINI RESPONSE:", result)
            return jsonify({
                "reply": "Sir, I received an empty response. Please try again."
            }), 502

        return jsonify({"reply": answer.strip()})

    except requests.exceptions.Timeout:
        return jsonify({
            "reply": "Sir, AI is taking too long. Please try again."
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
