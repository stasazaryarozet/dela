#!/usr/bin/env python3
"""
Cal.com Gate — максимальная интеграция

Требует: CAL_API_KEY (https://app.cal.com/settings/developer/api-keys)
"""

import os
import requests
from datetime import datetime, timezone


class CalcomGate:
    """Универсальный интерфейс к Cal.com API v2"""
    
    BASE_URL = 'https://api.cal.com/v2'
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('CAL_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "❌ CAL_API_KEY не найден.\n"
                "Получите: https://app.cal.com/settings/developer/api-keys\n"
                "Scopes: ВСЕ (максимум прав)"
            )
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    # === READ ===
    
    def get_me(self):
        """Получить информацию о пользователе"""
        response = requests.get(f'{self.BASE_URL}/me', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_event_types(self):
        """Получить все типы событий"""
        response = requests.get(f'{self.BASE_URL}/event-types', headers=self.headers)
        response.raise_for_status()
        data = response.json()
        # Flatten event types from groups
        event_types = []
        for group in data.get('data', {}).get('eventTypeGroups', []):
            event_types.extend(group.get('eventTypes', []))
        return event_types
    
    def get_event_type(self, event_type_id):
        """Получить конкретный event type"""
        response = requests.get(f'{self.BASE_URL}/event-types/{event_type_id}', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_event_type(self, event_type_id, **kwargs):
        """Обновить event type (description, title, length и т.д.)"""
        response = requests.patch(
            f'{self.BASE_URL}/event-types/{event_type_id}',
            headers=self.headers,
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def get_bookings(self, status=None):
        """Получить все бронирования"""
        params = {'status': status} if status else {}
        response = requests.get(f'{self.BASE_URL}/bookings', headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    # === WRITE ===
    
    def update_profile(self, username):
        """Обновить username профиля"""
        data = {'username': username}
        response = requests.patch(f'{self.BASE_URL}/me', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def create_event_type(self, title, slug, length_in_minutes=40, description=None):
        """Создать тип события"""
        data = {
            'title': title,
            'slug': slug,
            'lengthInMinutes': length_in_minutes,
            'description': description or title
        }
        response = requests.post(f'{self.BASE_URL}/event-types', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    # === EXPORT ===
    
    def export_substance(self):
        """Экспорт всех данных Cal.com"""
        me = self.get_me()
        event_types = self.get_event_types()
        bookings = self.get_bookings()
        
        substance = {
            'provider': 'calcom',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'user': me,
                'event_types': event_types,
                'bookings': bookings,
                'event_types_count': len(event_types),
                'bookings_count': len(bookings.get('data', []))
            }
        }
        
        return substance


if __name__ == '__main__':
    try:
        gate = CalcomGate()
        
        print("🔐 Cal.com Gate\n")
        
        me = gate.get_me()
        user = me.get('data', {})
        print(f"✅ Пользователь: {user.get('username', 'N/A')}")
        print(f"   Email: {user.get('email', 'N/A')}\n")
        
        event_types = gate.get_event_types()
        print(f"📅 Типы событий ({len(event_types)}):\n")
        
        for event in event_types:
            print(f"   • {event.get('title')} ({event.get('slug')})")
            print(f"     URL: https://cal.com/{user.get('username')}/{event.get('slug')}")
            if event.get('description'):
                print(f"     Description: {event.get('description')}")
        
        print(f"\n📊 Экспорт Substance...")
        substance = gate.export_substance()
        print(f"✅ Экспортировано:")
        print(f"   Event Types: {substance['data']['event_types_count']}")
        print(f"   Bookings: {substance['data']['bookings_count']}")
        
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Ошибка: {e}")
