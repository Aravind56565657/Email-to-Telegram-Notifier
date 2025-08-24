# Email-to-Telegram-Notifier

# 📧 Gmail Gemini Telegram Notifier

An intelligent Kivy desktop application that monitors your Gmail, summarizes and prioritizes your email with Google Gemini AI, and sends actionable notifications directly to Telegram.  
Also provides a live, color-coded dashboard view of your critical and urgent mails.

---

## 🚀 Features

- **Connects securely to your Gmail account** (OAuth2—your mail stays private)
- **Summarizes and classifies new emails using Google Gemini AI**
    - Detects important, urgent, task, due-soon, and overdue mails
- **Telegram bot integration**: sends smart, actionable notifications
- **Beautiful Kivy desktop UI** for Windows (scrollable dashboard, professional theme, and emoji/icons)
- **Manual and automatic background polling** — never miss important mail, even if you’re not watching your inbox!
- **Color-coded dashboard:** visually ranks urgency and status
- **Robust error handling** (no silent crashes)

---

## 🖥️ UI Preview

📧 Gmail → 🤖 Gemini → 📲 Telegram

[🔗 Connect to Gmail]

[📧 Unread Mails] [✅ Read Mails] [🛑 Spam Mails]

🔥 Smart Prioritized Emails
ID: ... Subject: ... Priority: Urgent/Important/Task/etc.
Action: ...
Summary: ...
✨ Built with Kivy, Gemini, Gmail API & Telegram API



---

## 📝 Requirements

- Python 3.8+
- [Kivy](https://kivy.org/) (`pip install kivy`)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [google-auth, google-auth-oauthlib, google-api-python-client](https://developers.google.com/gmail/api/quickstart/python)
- [requests](https://requests.readthedocs.io/)
- Gemini API client (you must provide the `summarize_email` function, see below)
- [Telegram Bot Token](https://core.telegram.org/bots#botfather)

---

## ⚡ Quickstart

1. **Clone / Download this repository**

2. **Install dependencies:**  


pip install kivy google-auth google-auth-oauthlib google-api-python-client python-dotenv requests


3. **Setup Gmail API:**  
 - Create `credentials.json` in your project root ([Google Setup Guide](https://developers.google.com/gmail/api/quickstart/python))
 - On first run, you will be prompted to authenticate

4. **Set up Telegram Bot:**  
 - Create bot and get bot token (via BotFather)
 - Get your `chat_id` (see: https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)
 - Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your:token
   TELEGRAM_CHAT_ID=123456789
   ```

5. **Directory structure:**  
 ```
 gmail_to_telegram_app/
 ├─ src/
 │   ├─ gmail_api.py
 │   ├─ telegram_api.py
 │   └─ gemini_api.py
 ├─ ui/
 │   └─ main_layout.kv
 ├─ .env
 ├─ credentials.json
 ├─ main.py
 └─ README.md
 ```

6. **Run the app:**  


python main.py

---

## 🧠 Custom AI Summarization

This app expects a Gemini API function `summarize_email(prompt, model=...)` in `src/gemini_api.py`.  
You must provide key/config to Gemini API, or you can use any other LLM you wish if you return rich summaries in this format.

---

## 🛠️ Usage

- **Connect to Gmail** using the button at the top.
- Use manual category buttons to check Unread, Read, or Spam—summaries go to Telegram and dashboard.
- The app will **auto-check every 5 minutes** (configurable) for new, actionable emails.
- **View important/urgent/task mails live** in the desktop dashboard, color-coded.
- **Get Telegram messages** for each important/task email instantly.

---

## 🌈 Customizing

- **Polling interval**: edit `interval_minutes` in `main.py`
- **Gemini prompts/categorization** can be edited (instructions in `main.py`)
- **Add more notification channels**: extend `telegram_api.py` or add other modules
- **UI/Theme tweaks**: edit `ui/main_layout.kv`

---

## ⚠️ Notes

- **Never share your secrets or `credentials.json` file** publicly!
- This is a demo/prototype for personal productivity—tune your AI prompts for best results.

---

## 👤 Author

Made by **Aravind Kumar**  
Want to make it even smarter or deploy for yourself/team? [Contact me!]

---

## ☑️ License

MIT License (customize if needed)

---

