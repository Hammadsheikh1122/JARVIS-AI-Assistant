
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

SYSTEM_INSTRUCTION = """
You are JARVIS, an intelligent personal AI assistant.

LANGUAGE RULES:
- English input: reply in natural English.
- Roman Urdu input: reply in natural Pakistani Roman Urdu.
- Use only English letters in the normal reply.
- Never use Urdu or Devanagari script in the normal reply.
- For mixed language, respond naturally in the same style.
- Be polite, concise and helpful.
- Address the user as sir when appropriate.
- Never pretend to complete an action you did not perform.
- Ask for confirmation before sensitive actions.
"""

VOICE_INSTRUCTION = """
You are a speech text converter for JARVIS.

Convert the supplied assistant response into text suitable for speech.

Rules:
1. If the response is English, keep it in natural English.
2. If the response is Roman Urdu, convert the Urdu words into
   natural Pakistani Urdu script.
3. Keep English technical words and names in English where appropriate.
4. Do not translate or change the meaning.
5. Return only the converted speech text.
"""

def ask_gemini(message, instruction):
    response = requests.post(
        GEMINI_URL,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        },
        json={
            "model": "gemini-3.5-flash-lite",
            "input": message,
            "system_instruction": instruction,
            "generation_config": {
                "temperature": 0.3,
                "max_output_tokens": 500
            }
        },
        timeout=60
    )

    response.raise_for_status()
    result = response.json()

    answer = ""

    for step in result.get("steps", []):
        if step.get("type") == "model_output":
            for part in step.get("content", []):
                if part.get("type") == "text":
                    answer += part.get("text", "")

    return answer.strip()


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

        reply = ask_gemini(user_message, SYSTEM_INSTRUCTION)

        if not reply:
            return jsonify({
                "reply": "Sir, I received an empty response."
            }), 502

        # Generate a separate version for spoken output.
        try:
            speech = ask_gemini(reply, VOICE_INSTRUCTION)
        except Exception as error:
            print("VOICE TEXT ERROR:", repr(error))
            speech = reply

        return jsonify({
            "reply": reply,
            "speech": speech or reply
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
