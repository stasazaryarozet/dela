#!/usr/bin/env python3
from calcom_gate import CalcomGateFull
from datetime import datetime, timedelta

gate = CalcomGateFull('cal_live_c7dba7d0cfbe9b741f496d56ef2f34e0')

# Получаем бронирования за ближайшие 2 недели
print("📅 Бронирования Cal.com:\n")
bookings = gate.get_bookings()

for booking in bookings.get('data', []):
    start = booking.get('startTime', '')
    title = booking.get('title', '')
    attendee = booking.get('attendeeName', '')
    
    if '2025-11-21' in start:
        print(f"✓ 21 ноября: {start}")
        print(f"  Название: {title}")
        print(f"  Участник: {attendee}\n")
