#!/usr/bin/env python3
"""
Включает полную историю для супергрупп, где она закрыта
"""
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import TogglePreHistoryHiddenRequest
import json

with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']
client = TelegramClient('olga_session', olga['api_id'], olga['api_hash'])

# Супергруппы, где история закрыта
TARGET_SUPERGROUPS = [
    -1002688231781,  # ДЕЛАЕМ
    -1003208406348,  # N, O, S
    -1002434489044,  # Лето 25 - Современное искусство
    -1002616923445,  # Лето 25 - Колористика
    -1002399539099,  # Зима 25 - Колористика
    -1002293661920,  # Архитектура и дизайн XX-XXI века
]

async def fix_history():
    await client.start(phone=olga['phone'])
    
    print("🔧 Открываю полную историю в супергруппах...\n")
    
    results = []
    for chat_id in TARGET_SUPERGROUPS:
        try:
            entity = await client.get_entity(chat_id)
            
            # Включаем полную историю
            await client(TogglePreHistoryHiddenRequest(
                channel=entity,
                enabled=False  # False = показывать всю историю
            ))
            
            print(f"✅ {entity.title}: история открыта")
            results.append({'name': entity.title, 'id': chat_id, 'status': 'fixed'})
            
        except Exception as e:
            print(f"❌ {chat_id}: {str(e)}")
            results.append({'id': chat_id, 'status': f'error: {str(e)}'})
    
    with open('telegram_supergroups_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Обработано супергрупп: {len(results)}")
    print("📄 Результаты: telegram_supergroups_fixed.json")

with client:
    client.loop.run_until_complete(fix_history())
