
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


SYSTEM_INSTRUCTION = """
You are JARVIS, an intelligent personal AI assistant.

LANGUAGE RULES — FOLLOW STRICTLY:

1. If the user speaks or writes in English, reply in natural English.

2. If the user writes in Roman Urdu or Roman English,
   reply in natural Pakistani Roman Urdu using ONLY English letters.

3. Roman Urdu means Urdu spoken in Pakistan but written using
   the English alphabet.

4. NEVER write Urdu using Urdu script.

5. NEVER write Hindi using Devanagari script.

6. If the user says:
   "Roman English mein baat karo"
   or
   "Roman Urdu mein baat karo"
   you MUST reply in Pakistani Roman Urdu using English letters.

7. Do not switch languages unnecessarily.

8. If the user mixes English and Roman Urdu,
   reply naturally in the same mixed style.

9. Use simple, natural Pakistani expressions.
   Examples:
   "Ji sir, main aapki madad kar sakta hoon."
   "Aap kya karna chahte hain?"
   "Bilkul sir, main samajh gaya."

10. Keep spoken answers clear, natural and easy to pronounce.

PERSONALITY:
- Your name is JARVIS.
- Be intelligent, polite and helpful.
- Address the user as sir when appropriate.
- Give accurate answers.
- Never pretend you completed an action that you did not perform.
- Ask for confirmation before sensitive actions.
- Keep answers concise unless the user requests details.
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "reply": "Please type a message."
            })

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
                "model": "gemini-3.5-flash-lite",
                "input": user_message,
                "system_instruction": SYSTEM_INSTRUCTION,
                "generation_config": {
                    "temperature": 0.4,
                    "max_output_tokens": 500
                }
            },
            timeout=60
        )

        if response.status_code != 200:
            print(
                "GEMINI ERROR:",
                response.status_code,
                response.text
            )

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

        return jsonify({
            "reply": answer.strip()
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "reply": "Sir, AI is taking too long. Please try again."
        }), 504

    except Exception as error:
        print("ERROR:", repr(error))

        return jsonify({
            "reply": "Sorry sir, something went wrong."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
    )
