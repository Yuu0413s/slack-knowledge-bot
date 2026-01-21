import os
from dotenv import load_dotenv
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google import genai

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
logging.basicConfig(level=logging.DEBUG)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("⚠️ GEMINI_API_KEYが設定されていません")

def call_gemini(user_input):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_input
        )
        return response.text
    except Exception as e:
        return f"エラー: {e}"

@app.command("/ask-bolty")
def handle_ask_bolty(ack, respond, command):
    ack()
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=command["text"]
        )
        respond(response.text)
    except Exception as e:
        respond(f"エラー: {e}")

@app.command("/uranai-bolty")
def handle_uranai_bolty(ack, respond, command):
    ack()
    try:
        user_input = command['text']

        if user_input:
            prompt = f"「{user_input}」の今日の運勢を楽しく占ってください。ラッキーアイテムも教えて。"
        else:
            prompt = "今日の全体的な運勢を楽しく占ってください。"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        respond(response.text)

    except Exception as e:
        respond(f"エラー: {e}")


@app.event("message")
def handle_message_events(body, say, logger):
    event = body["event"]

    if "bot_id" in event:
        return

    if event.get("channel_type") == "im":
        logger.info(body) # ログ用

        user_text = event["text"]

        reply = call_gemini(user_text)
        say(reply)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()