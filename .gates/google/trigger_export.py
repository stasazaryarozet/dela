#!/usr/bin/env python3
"""
Trigger Export — Событийная архитектура для экспорта Субстанции
Реагирует на события в реальном времени (Gmail, Calendar, Cal.com)
"""

from google_gate import GoogleGate
from export_substance import export_substance
import time
import json
from datetime import datetime

class SubstanceTrigger:
    """Отслеживает события и автоматически экспортирует Субстанцию"""
    
    def __init__(self):
        self.gate = GoogleGate()
        self.last_gmail_check = None
        self.last_calendar_check = None
        self.known_message_ids = set()
        self.known_event_ids = set()
    
    def initialize(self):
        """Первичная инициализация (запомнить текущее состояние)"""
        print("🔧 Инициализация триггеров...")
        
        # Gmail: запомнить текущие письма
        gmail = self.gate.gmail()
        results = gmail.users().messages().list(
            userId='me',
            maxResults=10,
            labelIds=['INBOX']
        ).execute()
        
        for msg in results.get('messages', []):
            self.known_message_ids.add(msg['id'])
        
        print(f"   ✓ Gmail: {len(self.known_message_ids)} писем в базе")
        
        # Calendar: запомнить текущие события
        from datetime import timedelta
        cal = self.gate.calendar()
        
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
        
        events_result = cal.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,
            singleEvents=True
        ).execute()
        
        for event in events_result.get('items', []):
            self.known_event_ids.add(event['id'])
        
        print(f"   ✓ Calendar: {len(self.known_event_ids)} событий в базе")
        print("✓ Инициализация завершена\n")
    
    def check_gmail(self):
        """Проверить новые письма"""
        gmail = self.gate.gmail()
        results = gmail.users().messages().list(
            userId='me',
            maxResults=10,
            labelIds=['INBOX']
        ).execute()
        
        new_messages = []
        for msg in results.get('messages', []):
            if msg['id'] not in self.known_message_ids:
                # Новое письмо
                m = gmail.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject']
                ).execute()
                
                headers = {h['name']: h['value'] for h in m['payload']['headers']}
                new_messages.append({
                    'id': msg['id'],
                    'from': headers.get('From', ''),
                    'subject': headers.get('Subject', '')
                })
                
                self.known_message_ids.add(msg['id'])
        
        return new_messages
    
    def check_calendar(self):
        """Проверить новые события"""
        from datetime import timedelta
        cal = self.gate.calendar()
        
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
        
        events_result = cal.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,
            singleEvents=True
        ).execute()
        
        new_events = []
        for event in events_result.get('items', []):
            if event['id'] not in self.known_event_ids:
                # Новое событие
                new_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', '(без названия)'),
                    'start': event['start'].get('dateTime', event['start'].get('date'))
                })
                
                self.known_event_ids.add(event['id'])
        
        return new_events
    
    def trigger_export(self, reason):
        """Выполнить экспорт Субстанции"""
        print(f"\n{'=' * 60}")
        print(f"🔔 ТРИГГЕР: {reason}")
        print(f"{'=' * 60}")
        
        substance = export_substance()
        
        # Сохранить с метаданными триггера
        output = {
            'trigger': {
                'timestamp': datetime.now().isoformat(),
                'reason': reason
            },
            'substance': substance
        }
        
        filename = f"substance_triggered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Субстанция экспортирована: {filename}")
        print(f"✓ Триггер: {reason}")
        print(f"{'=' * 60}\n")
        
        return filename
    
    def run(self, interval=60):
        """Запустить мониторинг (polling каждые N секунд)"""
        print("=" * 60)
        print("Trigger Export — Мониторинг событий")
        print("=" * 60)
        print(f"Интервал проверки: {interval} секунд")
        print("Нажмите Ctrl+C для остановки\n")
        
        self.initialize()
        
        try:
            while True:
                # Проверка Gmail
                new_messages = self.check_gmail()
                if new_messages:
                    for msg in new_messages:
                        reason = f"Новое письмо: {msg['subject']} (от {msg['from']})"
                        self.trigger_export(reason)
                
                # Проверка Calendar
                new_events = self.check_calendar()
                if new_events:
                    for event in new_events:
                        reason = f"Новое событие: {event['summary']} ({event['start']})"
                        self.trigger_export(reason)
                
                # Ждать до следующей проверки
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n✓ Мониторинг остановлен")

if __name__ == "__main__":
    trigger = SubstanceTrigger()
    trigger.run(interval=300)  # Проверка каждые 5 минут
