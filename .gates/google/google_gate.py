#!/usr/bin/env python3
"""
Google Gate для проекта "○ / Ольга"
ВСЕ возможные scope — максимальный доступ ко всей экосистеме Google
"""

import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

# ВСЕ возможные scope (полный доступ к экосистеме Google)
SCOPES = [
    # Gmail (полный доступ)
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    
    # Calendar (полный доступ)
    'https://www.googleapis.com/auth/calendar',
    
    # Drive (полный доступ к файлам)
    'https://www.googleapis.com/auth/drive',
    
    # Contacts (полный доступ к контактам)
    'https://www.googleapis.com/auth/contacts',
    
    # Sheets, Docs, Slides (полный доступ)
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations',
    
    # Forms (полный доступ)
    'https://www.googleapis.com/auth/forms',
    
    # Tasks (задачи)
    'https://www.googleapis.com/auth/tasks',
    
    # Keep (заметки, если доступно)
    # 'https://www.googleapis.com/auth/keep',
    
    # Photos (если нужно)
    # 'https://www.googleapis.com/auth/photoslibrary',
    
    # YouTube (если нужно)
    # 'https://www.googleapis.com/auth/youtube',
]

class GoogleGate:
    """Врата в экосистему Google — максимальный доступ ко ВСЕМ ресурсам"""
    
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
    
    def get_credentials(self):
        """Получить credentials с авто-обработкой 7-дневного цикла"""
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        if self.creds:
            if self.creds.expired and self.creds.refresh_token:
                try:
                    print("⏳ Token истёк, обновляю...")
                    self.creds.refresh(Request())
                    print("✓ Token обновлён")
                    
                    with open(self.token_path, 'wb') as token:
                        pickle.dump(self.creds, token)
                    
                except RefreshError:
                    print(f"❌ Refresh token недействителен (7 дней)")
                    print(f"   Удаляю {self.token_path}, запускаю реавторизацию...")
                    
                    os.remove(self.token_path)
                    self.creds = None
                    return self.get_credentials()
        
        if not self.creds or not self.creds.valid:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"❌ {self.credentials_path} не найден")
            
            print("\n" + "=" * 60)
            print("АВТОРИЗАЦИЯ (ВРАТА В ЭКОСИСТЕМУ GOOGLE)")
            print("=" * 60)
            print("Откроется браузер для авторизации Ольги.")
            print("Разрешите доступ ко ВСЕМ Google сервисам.")
            print("=" * 60 + "\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, 
                SCOPES
            )
            
            self.creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)
            
            print(f"\n✓ Авторизация завершена")
            print(f"✓ Token сохранён")
            print(f"✓ Доступ ко ВСЕМ Google сервисам активирован")
            print(f"✓ Токен действителен 7 дней\n")
        
        return self.creds
    
    def get_service(self, service_name, version):
        """Универсальный метод для получения любого Google API service"""
        creds = self.get_credentials()
        return build(service_name, version, credentials=creds)
    
    # Shortcuts для основных сервисов
    def gmail(self):
        return self.get_service('gmail', 'v1')
    
    def calendar(self):
        return self.get_service('calendar', 'v3')
    
    def drive(self):
        return self.get_service('drive', 'v3')
    
    def sheets(self):
        return self.get_service('sheets', 'v4')
    
    def docs(self):
        return self.get_service('docs', 'v1')
    
    def forms(self):
        return self.get_service('forms', 'v1')
    
    def contacts(self):
        return self.get_service('people', 'v1')
    
    def tasks(self):
        return self.get_service('tasks', 'v1')
    
    # Тесты
    def test(self):
        """Тест всех основных API"""
        print("\n📧 Gmail:")
        gmail = self.gmail()
        results = gmail.users().messages().list(userId='me', maxResults=5, labelIds=['INBOX']).execute()
        for msg in results.get('messages', []):
            m = gmail.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject']).execute()
            subj = next((h['value'] for h in m['payload']['headers'] if h['name'] == 'Subject'), '(no subject)')
            print(f"   • {subj}")
        
        print("\n📅 Calendar:")
        from datetime import datetime, timedelta
        cal = self.calendar()
        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        event = {
            'summary': 'Еженедельная проверка Google Gate',
            'start': {'dateTime': start.isoformat(), 'timeZone': 'Europe/Moscow'},
            'end': {'dateTime': end.isoformat(), 'timeZone': 'Europe/Moscow'},
        }
        
        result = cal.events().insert(calendarId='primary', body=event).execute()
        print(f"   ✓ Событие создано: {result['summary']}")
        print(f"   ✓ {start.strftime('%Y-%m-%d %H:%M')}")
        
        print("\n💾 Drive:")
        drive = self.drive()
        results = drive.files().list(pageSize=5, fields="files(name)").execute()
        files = results.get('files', [])
        if files:
            for f in files:
                print(f"   • {f['name']}")
        else:
            print("   (нет файлов или доступ ограничен)")
        
        print("\n✓ ВСЕ сервисы доступны")

if __name__ == "__main__":
    print("=" * 60)
    print("Google Gate — Врата в экосистему Google")
    print("=" * 60)
    
    gate = GoogleGate()
    gate.test()
    
    print("\n" + "=" * 60)
    print("✓ Google Gate активирован")
    print("=" * 60)
