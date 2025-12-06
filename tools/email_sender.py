#!/usr/bin/env python3
"""
Email Sender Tool.
Wraps the Google Gate (Gmail API) to provide simple email sending capabilities.
Usage:
    from email_sender import send_email
    send_email("recipient@example.com", "Subject", "<h1>Body</h1>")
"""
import sys
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ensure tools is in path
TOOLS_DIR = Path(__file__).parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from context import Context
except ImportError:
    # Context should be in tools/
    pass

# Initialize Context
try:
    CTX = Context(__file__)
    # Resolve path to credentials.json
    # Root is typically up one level from tools/, then .gates/secrets/google/credentials.json
    ROOT = Path(__file__).parent.parent
    CREDENTIALS_PATH = ROOT / '.gates' / 'secrets' / 'google' / 'credentials.json'
    
    # Initialize Google Gate with specific credentials path
    # We must access the Class from the module loaded by gate()
    google_mod = CTX.gate('google')
    GOOGLE = google_mod.GoogleGate(credentials_path=str(CREDENTIALS_PATH))
except Exception as e:
    print(f"Error initializing Context/Google Gate: {e}")
    sys.exit(1)

def send_email(to_email, subject, body_html, from_email="me"):
    """
    Sends an email using Gmail API.
    """
    service = GOOGLE.gmail()
    
    message = MIMEMultipart()
    message['to'] = to_email
    message['from'] = from_email
    message['subject'] = subject
    
    msg = MIMEText(body_html, 'html')
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    body = {'raw': raw_message}
    
    try:
        sent_message = service.users().messages().send(userId=from_email, body=body).execute()
        print(f"✅ Email sent to {to_email}. ID: {sent_message['id']}")
        return sent_message
    except Exception as e:
        print(f"❌ Failed to email {to_email}: {e}")
        return None

if __name__ == "__main__":
    # Test execution
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
        send_email(recipient, "Test from Dela System", "<h1>Hello from Context!</h1><p>Integration verified.</p>")
    else:
        print("Usage: python3 email_sender.py <recipient_email>")
