from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import os
import json
from dotenv import load_dotenv
import datetime
import re

from src.telegram_api import TelegramNotifier
from src.gmail_api import GmailAPI
from src.gemini_api import summarize_email

# Load environment variables
load_dotenv()

# Load the .kv UI for GmailTelegramApp
kv_path = os.path.join(os.path.dirname(__file__), "ui", "main_layout.kv")
Builder.load_file(kv_path)

class GmailTelegramApp(BoxLayout):
    status_text = StringProperty("App initialized. Ready to test.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gmail = None
        self.telegram = TelegramNotifier()
        self.processed_ids = set()
        self.summary_blocks = []

    def connect_gmail(self):
        try:
            self.status_text = '🔄 Connecting to Gmail...'
            self.gmail = GmailAPI()
            self.status_text = '✅ Gmail connected successfully!'
            self.start_auto_check()
        except Exception as e:
            self.status_text = f'❌ Gmail connection failed: {str(e)}'

    def start_auto_check(self, interval_minutes=5):
        self.status_text = f'🔔 Auto-check enabled (every {interval_minutes} min)'
        Clock.schedule_interval(lambda dt: self.auto_check_importants(), interval_minutes * 60)

    def auto_check_importants(self):
        if not self.gmail:
            self.status_text = '🔗 Please connect to Gmail for auto-check!'
            return

        try:
            emails = self.gmail.query_mails(query="is:unread in:inbox", max_results=20)
            if not emails:
                self.update_dashboard([])
                return

            email_json_list = []
            found_new = False
            for email in emails:
                if email['id'] not in self.processed_ids:
                    found_new = True
                    status = 'UNREAD' if 'UNREAD' in (email.get('labels', [])) else 'READ'
                    email_json_list.append({
                        'id': email['id'],
                        'from': email['sender'],
                        'subject': email['subject'],
                        'date': email['date'],
                        'status': status,
                        'preview': email['snippet']
                    })
                    self.processed_ids.add(email['id'])

            if not found_new:
                return

            prompt = (
                "You are a brilliant assistant for email. Below is a list (JSON array) of email metadata. "
                "Each object has: id, from, subject, date, status (READ/UNREAD), and preview (the first part of the email body).\n"
                "For each email, decide if it is important, urgent, a task, due soon, or past due. "
                "For each valuable email, output exactly in this format and put TWO blank lines between:\n"
                "ID: ...\nFrom: ...\nSubject: ...\nDate: ...\nPriority: ...\nAction: ...\nSummary: ...\n\n"
                "ONLY return those blocks; nothing else. Double newlines between blocks. Respond with empty text if none.\n"
                f"Today's date is: {datetime.date.today()}.\n"
                f"Emails:\n{json.dumps(email_json_list, indent=2)}"
            )
            output = summarize_email(prompt, model="models/gemini-1.5-pro-latest")
            print("[AUTO] Gemini's auto-check output:", repr(output))

            summaries = []
            notified = 0
            for block in re.split(r'\n{2,}', output):
                s = block.strip()
                if s:
                    self.telegram.send_message(s)
                    summaries.append(s)
                    notified += 1
            self.update_dashboard(summaries)
            if notified:
                self.status_text = f"✅ Auto: Sent {notified} priority email notification(s)"
        except Exception as e:
            self.status_text = f'❌ Auto-check error: {str(e)}'

    def process_mails(self, category):
        if not self.gmail:
            self.status_text = '🔗 Please connect to Gmail first!'
            return

        try:
            if category == 'unread':
                self.status_text = '🔎 Fetching unread emails...'
                emails = self.gmail.query_mails(query="is:unread in:inbox", max_results=20)
            elif category == 'read':
                self.status_text = '🔎 Fetching read emails...'
                emails = self.gmail.query_mails(query="is:read in:inbox", max_results=20)
            elif category == 'spam':
                self.status_text = '🔎 Fetching spam emails...'
                emails = self.gmail.query_mails(query="in:spam", max_results=20)
            else:
                self.status_text = '❓ Unknown category!'
                self.update_dashboard([])
                return

            if not emails:
                self.status_text = f'🛑 No {category} emails found.'
                self.update_dashboard([])
                return

            email_json_list = []
            for email in emails:
                status = 'UNREAD' if 'UNREAD' in (email.get('labels', [])) else 'READ'
                email_json_list.append({
                    'id': email['id'],
                    'from': email['sender'],
                    'subject': email['subject'],
                    'date': email['date'],
                    'status': status,
                    'preview': email['snippet']
                })
            prompt = (
                "You are a brilliant assistant for email. Below is a list (JSON array) of email metadata. "
                "Each object has: id, from, subject, date, status (READ/UNREAD), and preview (the first part of the email body).\n"
                "For each email, decide:\n"
                "- Is it 'important', 'urgent', a 'task', due soon, past due?\n"
                "- For each high-value email, output a separate block in exactly this format—and put TWO blank lines between blocks for splitting:\n"
                "ID: ...\nFrom: ...\nSubject: ...\nDate: ...\nPriority: ...\nAction: ...\nSummary: ...\n\n"
                "ONLY return those blocks—no intro, no explanations. Double newlines between blocks. Respond with empty text if none.\n"
                f"Today's date is: {datetime.date.today()}.\n"
                f"Emails:\n{json.dumps(email_json_list, indent=2)}"
            )
            output = summarize_email(prompt, model="models/gemini-1.5-pro-latest")
            print(f"Gemini's raw output:\n{repr(output)}")

            summaries = []
            notified = 0
            for block in re.split(r'\n{2,}', output):
                s = block.strip()
                if s:
                    self.telegram.send_message(s)
                    summaries.append(s)
                    notified += 1
            self.update_dashboard(summaries)
            if notified:
                self.status_text = f"✅ Sent {notified} priority {category} email notifications!"
            else:
                self.status_text = f"🛑 No actionable {category} emails found."
        except Exception as e:
            self.status_text = f'❌ Error processing {category} emails: {str(e)}'
            self.update_dashboard([])

    def update_dashboard(self, summaries):
        mail_list = self.ids.mail_list
        items = []
        # If nothing to show, always set a valid item with all expected keys!
        if not summaries:
            items = [{
                "summary_text": "No actionable or high-priority emails found.",
                "bg_color": (0.13, 0.16, 0.19, 1),
                "text_color": (0.8, 0.8, 0.8, 1)
            }]
            mail_list.data = items
            return
        for s in summaries:
            lower = s.lower()
            if "urgent" in lower:
                bg = (0.8, 0.22, 0.22, 1); fg = (1, 1, 1, 1)
            elif "important" in lower:
                bg = (0.22, 0.5, 0.9, 1); fg = (1, 1, 1, 1)
            elif "due soon" in lower:
                bg = (0.94, 0.6, 0.25, 1); fg = (1, 1, 1, 1)
            elif "task" in lower:
                bg = (0.96, 0.92, 0.33, 1); fg = (0.22, 0.22, 0.22, 1)
            elif "past due" in lower or "overdue" in lower:
                bg = (0.57, 0.16, 0.31, 1); fg = (1, 1, 1, 1)
            else:
                bg = (0.14, 0.18, 0.25, 1); fg = (1, 1, 1, 1)
            items.append({"summary_text": s, "bg_color": bg, "text_color": fg})
        mail_list.data = items


class MainApp(App):
    def build(self):
        self.title = "Gmail Gemini Telegram Notifier"
        return GmailTelegramApp()

if __name__ == '__main__':
    MainApp().run()
