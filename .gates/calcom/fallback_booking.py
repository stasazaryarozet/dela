#!/usr/bin/env python3
"""
Fallback Calendar Booking System для Ольги
Архитектурное решение для бронирования когда Cal.com недоступен
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class OlgaBookingFallback:
    """Резервная система бронирования через Google Calendar + Email"""
    
    def __init__(self):
        self.bookings_file = Path(__file__).parent / 'fallback_bookings.json'
        self.load_bookings()
    
    def load_bookings(self):
        """Загрузить существующие бронирования"""
        if self.bookings_file.exists():
            with open(self.bookings_file, 'r', encoding='utf-8') as f:
                self.bookings = json.load(f)
        else:
            self.bookings = []
    
    def save_bookings(self):
        """Сохранить бронирования"""
        with open(self.bookings_file, 'wb') as f:
            f.write(json.dumps(self.bookings, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def get_available_slots(self, days_ahead=14):
        """Получить доступные слоты из Google Calendar"""
        try:
            # Импортируем Google Gate
            import sys
            google_gate_path = str(Path(__file__).parent.parent / 'google')
            if google_gate_path not in sys.path:
                sys.path.insert(0, google_gate_path)
            
            # Меняем рабочую директорию для правильного поиска credentials
            original_cwd = os.getcwd()
            os.chdir(google_gate_path)
            
            try:
                from google_gate import GoogleGate
                
                gate = GoogleGate()
                cal = gate.calendar()
                
                # Получаем события на N дней вперед
                from datetime import timezone
                now = datetime.now(timezone.utc)
                time_min = now.isoformat()
                time_max = (now + timedelta(days=days_ahead)).isoformat()
                
                events_result = cal.events().list(
                    calendarId='primary',
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                # Фильтруем события со слотами
                available_slots = []
                for event in events_result.get('items', []):
                    summary = event.get('summary', '')
                    if '🔓 СЛОТ' in summary or 'SLOT' in summary.upper():
                        start = event['start'].get('dateTime')
                        end = event['end'].get('dateTime')
                        
                        # Проверяем, не забронирован ли уже
                        event_id = event['id']
                        is_booked = any(b['event_id'] == event_id for b in self.bookings)
                        
                        if not is_booked:
                            available_slots.append({
                                'event_id': event_id,
                                'start': start,
                                'end': end,
                                'summary': summary
                            })
                
                return available_slots
                
            finally:
                os.chdir(original_cwd)
            
        except Exception as e:
            print(f"❌ Ошибка получения слотов из Google Calendar: {e}")
            return []
    
    def book_slot(self, event_id: str, client_name: str, client_email: str, client_phone: str = None):
        """Забронировать слот"""
        # Получаем информацию о слоте
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent / 'google'))
            from google_gate import GoogleGate
            
            gate = GoogleGate()
            cal = gate.calendar()
            
            # Получаем событие
            event = cal.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Обновляем название события
            original_summary = event.get('summary', '')
            event['summary'] = f"✅ {client_name} — Включить в дело"
            
            # Добавляем описание с контактами
            description = f"""
Бронирование через Fallback System

Клиент: {client_name}
Email: {client_email}
"""
            if client_phone:
                description += f"Телефон: {client_phone}\n"
            
            description += f"\nИсходное название: {original_summary}"
            event['description'] = description
            
            # Обновляем событие в Google Calendar
            updated_event = cal.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            # Сохраняем в локальную базу
            booking = {
                'booking_id': f"FALLBACK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'event_id': event_id,
                'client_name': client_name,
                'client_email': client_email,
                'client_phone': client_phone,
                'start': event['start'].get('dateTime'),
                'end': event['end'].get('dateTime'),
                'created_at': datetime.now().isoformat(),
                'status': 'confirmed'
            }
            
            self.bookings.append(booking)
            self.save_bookings()
            
            # Отправляем уведомления
            self.send_confirmation_email(booking)
            self.notify_olga(booking)
            
            return booking
            
        except Exception as e:
            print(f"❌ Ошибка бронирования: {e}")
            return None
    
    def send_confirmation_email(self, booking):
        """Отправить подтверждение клиенту"""
        # TODO: Реализовать через Gmail API или SMTP
        print(f"📧 Отправка подтверждения на {booking['client_email']}")
        
        subject = "✅ Бронирование подтверждено — Включить в дело с Ольгой Розет"
        
        body = f"""
Здравствуйте, {booking['client_name']}!

Ваше бронирование подтверждено.

📅 Дата: {booking['start']}
⏱ Длительность: 40 минут
👤 С: Ольгой Розет

Встреча пройдет онлайн. За день до встречи вы получите ссылку.

Вопросы: @olgarozet (Telegram) или o.g.rozet@gmail.com

—
Нет денег? Возможно, что-нибудь придумаем. Пожалуйста, пишите.
"""
        
        # В продакшене отправляется через Gmail API
        print(body)
    
    def notify_olga(self, booking):
        """Уведомить Ольгу о новом бронировании"""
        # Отправка в Telegram через бота
        print(f"📱 Уведомление Ольге о бронировании: {booking['client_name']}")
        
        try:
            # TODO: Интеграция с Telegram Bot
            message = f"""
🔔 Новое бронирование (Fallback)

👤 {booking['client_name']}
📧 {booking['client_email']}
📅 {booking['start']}
🆔 {booking['booking_id']}

Событие обновлено в Google Calendar.
"""
            print(message)
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления: {e}")
    
    def cancel_booking(self, booking_id: str):
        """Отменить бронирование"""
        booking = next((b for b in self.bookings if b['booking_id'] == booking_id), None)
        
        if not booking:
            return False
        
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent / 'google'))
            from google_gate import GoogleGate
            
            gate = GoogleGate()
            cal = gate.calendar()
            
            # Возвращаем исходное название события
            event = cal.events().get(calendarId='primary', eventId=booking['event_id']).execute()
            event['summary'] = '🔓 СЛОТ: Включить в дело (40 мин)'
            event['description'] = ''
            
            cal.events().update(
                calendarId='primary',
                eventId=booking['event_id'],
                body=event
            ).execute()
            
            # Обновляем статус
            booking['status'] = 'cancelled'
            booking['cancelled_at'] = datetime.now().isoformat()
            self.save_bookings()
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отмены: {e}")
            return False


if __name__ == '__main__':
    # Тестирование
    fallback = OlgaBookingFallback()
    
    print("=" * 60)
    print("FALLBACK BOOKING SYSTEM — Ольга Розет")
    print("=" * 60)
    
    # Получаем доступные слоты
    slots = fallback.get_available_slots()
    
    if slots:
        print(f"\n✅ Найдено доступных слотов: {len(slots)}\n")
        for i, slot in enumerate(slots, 1):
            print(f"{i}. {slot['start']} — {slot['summary']}")
    else:
        print("\n⚠️ Нет доступных слотов")
    
    print(f"\n📊 Всего бронирований: {len(fallback.bookings)}")

