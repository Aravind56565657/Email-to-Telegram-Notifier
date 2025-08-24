import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class TelegramNotifier:
    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text):
        if not self.bot_token or not self.chat_id:
            print("Telegram credentials not set!")
            return False
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            resp = requests.post(url, data=data, timeout=10)
            if resp.status_code == 200:
                print(f"[Telegram] Sent: {text[:40]}...")
                return True
            else:
                print(f"[Telegram] Error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            print(f"[Telegram] Exception: {e}")
            return False
