#!/usr/bin/env python3
"""
Export Substance — Экспорт Субстанции для Gemini
Извлекает всю доступную информацию из Google Gate
"""

from google_gate import GoogleGate
from datetime import datetime, timedelta
import json

def export_substance():
    """Создать полный срез Субстанции Google"""
    gate = GoogleGate()
    
    substance = {
        "timestamp": datetime.now().isoformat(),
        "gmail": {},
        "calendar": {},
        "drive": {},
        "contacts": {}
    }
    
    # Gmail: последние 20 писем
    print("📧 Экспорт Gmail...")
    gmail = gate.gmail()
    results = gmail.users().messages().list(
        userId='me', 
        maxResults=20,
        labelIds=['INBOX']
    ).execute()
    
    messages = []
    for msg in results.get('messages', []):
        m = gmail.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'To', 'Subject', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in m['payload']['headers']}
        messages.append({
            'id': msg['id'],
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'date': headers.get('Date', '')
        })
    
    substance['gmail']['recent_messages'] = messages
    
    # Calendar: события на следующие 30 дней
    print("📅 Экспорт Calendar...")
    cal = gate.calendar()
    
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=30)).isoformat() + 'Z'
    
    events_result = cal.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        maxResults=50,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = []
    for event in events_result.get('items', []):
        events.append({
            'id': event['id'],
            'summary': event.get('summary', '(без названия)'),
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'end': event['end'].get('dateTime', event['end'].get('date')),
            'attendees': [a.get('email') for a in event.get('attendees', [])]
        })
    
    substance['calendar']['upcoming_events'] = events
    
    # Drive: последние 20 файлов
    print("💾 Экспорт Drive...")
    drive = gate.drive()
    
    files_result = drive.files().list(
        pageSize=20,
        orderBy='modifiedTime desc',
        fields="files(id, name, mimeType, modifiedTime, webViewLink)"
    ).execute()
    
    files = []
    for f in files_result.get('files', []):
        files.append({
            'id': f['id'],
            'name': f['name'],
            'type': f['mimeType'],
            'modified': f['modifiedTime'],
            'link': f.get('webViewLink', '')
        })
    
    substance['drive']['recent_files'] = files
    
    # Contacts: первые 50 контактов
    print("👥 Экспорт Contacts...")
    people = gate.contacts()
    
    contacts_result = people.people().connections().list(
        resourceName='people/me',
        pageSize=50,
        personFields='names,emailAddresses,phoneNumbers'
    ).execute()
    
    contacts = []
    for person in contacts_result.get('connections', []):
        contact = {}
        
        if 'names' in person:
            contact['name'] = person['names'][0].get('displayName', '')
        
        if 'emailAddresses' in person:
            contact['emails'] = [e['value'] for e in person['emailAddresses']]
        
        if 'phoneNumbers' in person:
            contact['phones'] = [p['value'] for p in person['phoneNumbers']]
        
        contacts.append(contact)
    
    substance['contacts']['people'] = contacts
    
    return substance

if __name__ == "__main__":
    print("=" * 60)
    print("Экспорт Субстанции Google")
    print("=" * 60)
    
    substance = export_substance()
    
    # Сохранить в JSON
    output_file = f"substance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(substance, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Субстанция экспортирована: {output_file}")
    print(f"✓ Писем: {len(substance['gmail']['recent_messages'])}")
    print(f"✓ Событий: {len(substance['calendar']['upcoming_events'])}")
    print(f"✓ Файлов: {len(substance['drive']['recent_files'])}")
    print(f"✓ Контактов: {len(substance['contacts']['people'])}")
    print("=" * 60)
