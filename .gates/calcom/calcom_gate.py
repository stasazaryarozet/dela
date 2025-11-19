#!/usr/bin/env python3
"""
Cal.com Gate FULL — максимальная интеграция

Все endpoints из https://cal.com/docs/api-reference/
"""

import os
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any


class CalcomGateFull:
    """Полная интеграция Cal.com API v2"""
    
    BASE_URL = 'https://api.cal.com/v2'
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('CAL_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "❌ CAL_API_KEY не найден.\n"
                "Получите: https://app.cal.com/settings/developer/api-keys"
            )
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    # === ME ===
    
    def get_me(self) -> Dict:
        """GET /v2/me - информация о пользователе"""
        response = requests.get(f'{self.BASE_URL}/me', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_me(self, **kwargs) -> Dict:
        """PATCH /v2/me - обновить профиль"""
        response = requests.patch(f'{self.BASE_URL}/me', headers=self.headers, json=kwargs)
        response.raise_for_status()
        return response.json()
    
    # === EVENT TYPES ===
    
    def get_event_types(self) -> List[Dict]:
        """GET /v2/event-types - все типы событий"""
        response = requests.get(f'{self.BASE_URL}/event-types', headers=self.headers)
        response.raise_for_status()
        data = response.json()
        event_types = []
        for group in data.get('data', {}).get('eventTypeGroups', []):
            event_types.extend(group.get('eventTypes', []))
        return event_types
    
    def get_event_type(self, event_type_id: int) -> Dict:
        """GET /v2/event-types/{id}"""
        response = requests.get(f'{self.BASE_URL}/event-types/{event_type_id}', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_event_type(self, title: str, slug: str, length: int, **kwargs) -> Dict:
        """POST /v2/event-types - создать event type"""
        data = {'title': title, 'slug': slug, 'lengthInMinutes': length, **kwargs}
        response = requests.post(f'{self.BASE_URL}/event-types', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_event_type(self, event_type_id: int, **kwargs) -> Dict:
        """PATCH /v2/event-types/{id}"""
        response = requests.patch(
            f'{self.BASE_URL}/event-types/{event_type_id}',
            headers=self.headers,
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def delete_event_type(self, event_type_id: int) -> Dict:
        """DELETE /v2/event-types/{id}"""
        response = requests.delete(f'{self.BASE_URL}/event-types/{event_type_id}', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    # === BOOKINGS ===
    
    def get_bookings(self, status: Optional[str] = None, **params) -> Dict:
        """GET /v2/bookings - все бронирования"""
        if status:
            params['status'] = status
        response = requests.get(f'{self.BASE_URL}/bookings', headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_booking(self, uid: str) -> Dict:
        """GET /v2/bookings/{uid}"""
        response = requests.get(f'{self.BASE_URL}/bookings/{uid}', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_booking(self, event_type_id: int, start: str, attendee: Dict, **kwargs) -> Dict:
        """POST /v2/bookings - создать бронирование
        
        Args:
            event_type_id: ID типа события
            start: ISO datetime начала
            attendee: {"name": "...", "email": "...", "timeZone": "..."}
        """
        data = {
            'eventTypeId': event_type_id,
            'start': start,
            'attendee': attendee,
            **kwargs
        }
        response = requests.post(f'{self.BASE_URL}/bookings', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def cancel_booking(self, uid: str, reason: Optional[str] = None) -> Dict:
        """POST /v2/bookings/{uid}/cancel"""
        data = {'reason': reason} if reason else {}
        response = requests.post(f'{self.BASE_URL}/bookings/{uid}/cancel', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def reschedule_booking(self, uid: str, start: str, reason: Optional[str] = None) -> Dict:
        """POST /v2/bookings/{uid}/reschedule"""
        data = {'start': start}
        if reason:
            data['reason'] = reason
        response = requests.post(f'{self.BASE_URL}/bookings/{uid}/reschedule', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    # === SCHEDULES ===
    
    def get_schedules(self) -> Dict:
        """GET /v2/schedules"""
        response = requests.get(f'{self.BASE_URL}/schedules', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_schedule(self, schedule_id: int) -> Dict:
        """GET /v2/schedules/{id}"""
        response = requests.get(f'{self.BASE_URL}/schedules/{schedule_id}', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_schedule(self, name: str, time_zone: str, **kwargs) -> Dict:
        """POST /v2/schedules"""
        data = {'name': name, 'timeZone': time_zone, **kwargs}
        response = requests.post(f'{self.BASE_URL}/schedules', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_schedule(self, schedule_id: int, **kwargs) -> Dict:
        """PATCH /v2/schedules/{id}"""
        response = requests.patch(f'{self.BASE_URL}/schedules/{schedule_id}', headers=self.headers, json=kwargs)
        response.raise_for_status()
        return response.json()
    
    def delete_schedule(self, schedule_id: int) -> Dict:
        """DELETE /v2/schedules/{id}"""
        response = requests.delete(f'{self.BASE_URL}/schedules/{schedule_id}', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    # === SLOTS ===
    
    def get_available_slots(self, event_type_id: int, start_time: str, end_time: str, **params) -> Dict:
        """GET /v2/slots - доступные слоты"""
        params.update({
            'eventTypeId': event_type_id,
            'startTime': start_time,
            'endTime': end_time
        })
        response = requests.get(f'{self.BASE_URL}/slots', headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def reserve_slot(self, event_type_id: int, slot_time: str) -> Dict:
        """POST /v2/slots/reserve"""
        data = {'eventTypeId': event_type_id, 'slotTime': slot_time}
        response = requests.post(f'{self.BASE_URL}/slots/reserve', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    # === WEBHOOKS ===
    
    def get_webhooks(self) -> Dict:
        """GET /v2/webhooks"""
        response = requests.get(f'{self.BASE_URL}/webhooks', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_webhook(self, subscriber_url: str, event_triggers: List[str], **kwargs) -> Dict:
        """POST /v2/webhooks
        
        event_triggers: ["BOOKING_CREATED", "BOOKING_CANCELLED", "BOOKING_RESCHEDULED", etc]
        """
        data = {
            'subscriberUrl': subscriber_url,
            'eventTriggers': event_triggers,
            **kwargs
        }
        response = requests.post(f'{self.BASE_URL}/webhooks', headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete_webhook(self, webhook_id: str) -> Dict:
        """DELETE /v2/webhooks/{id}"""
        response = requests.delete(f'{self.BASE_URL}/webhooks/{webhook_id}', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    # === CALENDARS ===
    
    def get_calendars(self) -> Dict:
        """GET /v2/calendars"""
        response = requests.get(f'{self.BASE_URL}/calendars', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_busy_times(self, calendars_to_load: List[str], date_from: str, date_to: str) -> Dict:
        """GET /v2/calendars/busy-times"""
        params = {
            'calendarsToLoad': ','.join(calendars_to_load),
            'dateFrom': date_from,
            'dateTo': date_to
        }
        response = requests.get(f'{self.BASE_URL}/calendars/busy-times', headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    # === EXPORT SUBSTANCE ===
    
    def export_substance(self) -> Dict:
        """Экспорт всех данных Cal.com"""
        me = self.get_me()
        event_types = self.get_event_types()
        bookings = self.get_bookings()
        schedules = self.get_schedules()
        webhooks = self.get_webhooks()
        
        return {
            'provider': 'calcom',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'user': me,
                'event_types': event_types,
                'bookings': bookings.get('data', []),
                'schedules': schedules,
                'webhooks': webhooks,
                'counts': {
                    'event_types': len(event_types),
                    'bookings': len(bookings.get('data', [])),
                    'schedules': len(schedules.get('data', [])),
                    'webhooks': len(webhooks.get('data', []))
                }
            }
        }


if __name__ == '__main__':
    try:
        gate = CalcomGateFull()
        
        print("🔐 Cal.com Gate FULL\n")
        
        me = gate.get_me()
        user = me.get('data', {})
        print(f"✅ Пользователь: {user.get('username')}")
        print(f"   Email: {user.get('email')}\n")
        
        substance = gate.export_substance()
        counts = substance['data']['counts']
        
        print("📊 Экспортировано:")
        print(f"   Event Types: {counts['event_types']}")
        print(f"   Bookings: {counts['bookings']}")
        print(f"   Schedules: {counts['schedules']}")
        print(f"   Webhooks: {counts['webhooks']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
