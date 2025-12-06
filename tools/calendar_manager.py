#!/usr/bin/env python3
"""
Calendar Manager Tool.
Wraps Google Calendar and Cal.com Gates.
Usage:
    from calendar_manager import add_google_event, list_google_events
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Ensure tools is in path
TOOLS_DIR = Path(__file__).parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from context import Context
except ImportError:
    pass

# Initialize Context & Gates
try:
    CTX = Context(__file__)
    
    # Resolve path to Google credentials
    ROOT = Path(__file__).parent.parent
    CREDENTIALS_PATH = ROOT / '.gates' / 'secrets' / 'google' / 'credentials.json'
    
    google_mod = CTX.gate('google')
    GOOGLE = google_mod.GoogleGate(credentials_path=str(CREDENTIALS_PATH))
    
    # Manually load Cal.com gate because it's in a subdir
    CALCOM_DIR = CTX.root / '.gates' / 'calcom'
    if str(CALCOM_DIR) not in sys.path:
        sys.path.insert(0, str(CALCOM_DIR))
    
    try:
        from calcom_gate import CalcomGateFull
        # Initialize with Env Var (should be loaded by context/env or assumes system env)
        # Note: In a real deploy, we might fetch this key from Google Secrets or .env
        cal_key = os.environ.get('CAL_API_KEY')
        CALCOM = CalcomGateFull(cal_key) if cal_key else None
        if not cal_key:
            print("⚠️ CAL_API_KEY not found. Cal.com integration disabled.")
    except ImportError:
        print("⚠️ Could not import calcom_gate. Is .gates/calcom present?")
        CALCOM = None

except Exception as e:
    print(f"Error initializing Context/Gates: {e}")
    sys.exit(1)

def add_google_event(summary, start_dt, end_dt=None, description=""):
    """
    Adds an event to Google Calendar (Primary).
    start_dt: datetime object
    end_dt: datetime object (defaults to start + 1h)
    """
    service = GOOGLE.calendar()
    
    if not end_dt:
        end_dt = start_dt + timedelta(hours=1)
        
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Moscow'},
    }
    
    res = service.events().insert(calendarId='primary', body=event).execute()
    print(f"✅ Event created: {res.get('htmlLink')}")
    return res

def list_google_events(count=10):
    """Lists upcoming events"""
    service = GOOGLE.calendar()
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=count, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event['summary']}")
    return events

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Google Calendar accessing...")
        list_google_events(3)
    else:
        print("Calendar Manager Ready. Use as library or run with 'test'.")
