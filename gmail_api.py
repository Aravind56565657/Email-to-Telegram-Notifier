import os
import re
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from email.utils import parsedate_to_datetime
from googleapiclient.discovery import build
import pytz

def parse_email(sender):
    match = re.search(r'<(.+?)>', sender)
    return match.group(1) if match else sender

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailAPI:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def query_mails(self, query, max_results=10):
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            email_list = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']).execute()
                labels = msg.get('labelIds', [])
                data = self.extract_email_data(msg)
                data['labels'] = labels
                email_list.append(data)
            return email_list
        except Exception as error:
            print(f'Gmail query error: {error}')
            return []

    def extract_email_data(self, message):
        headers = message['payload'].get('headers', [])
        raw_sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        sender = parse_email(raw_sender)
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        try:
            parsed_date = parsedate_to_datetime(date_str)
            india = pytz.timezone('Asia/Kolkata')
            if parsed_date.tzinfo is None:
                parsed_date = pytz.utc.localize(parsed_date)
            date_ist = parsed_date.astimezone(india)
            email_time = date_ist.strftime('%Y-%m-%d %I:%M %p IST')
        except Exception:
            email_time = date_str or "Unknown"
        snippet = message.get('snippet', '')
        return {
            'id': message['id'],
            'sender': sender,
            'subject': subject,
            'date': email_time,
            'snippet': snippet
        }
