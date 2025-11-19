#!/usr/bin/env python3
import sys
from calcom_gate import CalcomGateFull
from datetime import datetime, timedelta

gate = CalcomGateFull('cal_live_c7dba7d0cfbe9b741f496d56ef2f34e0')

# ID Event Type для "40 минут"
event_type_id = 3859146

# Ближайшие 7 дней
start = datetime.now().isoformat()
end = (datetime.now() + timedelta(days=7)).isoformat()

print("🔍 Проверяю доступные слоты для 'В Дело'...\n")

try:
    slots = gate.get_available_slots(event_type_id, start, end)
    print(f"📅 Найдено слотов: {len(slots.get('data', {}).get('slots', []))}\n")
    
    for slot in slots.get('data', {}).get('slots', [])[:5]:
        print(f"  • {slot.get('time')}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
