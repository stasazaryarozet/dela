#!/usr/bin/env python3
"""
Финальная проверка: статус истории во всех супергруппах
"""
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel
import json

with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']
client = TelegramClient('olga_session', olga['api_id'], olga['api_hash'])

async def final_check():
    await client.start(phone=olga['phone'])
    
    print("🔍 Финальная проверка всех супергрупп...\n")
    
    TARGET_IDS = [
        -1002688231781,  # ДЕЛАЕМ
        -1003208406348,  # N, O, S
        -1002434489044,  # Лето 25 - Современное искусство
        -1002616923445,  # Лето 25 - Колористика
        -1002399539099,  # Зима 25 - Колористика
        -1002293661920,  # Архитектура и дизайн XX-XXI века
    ]
    
    results = []
    for chat_id in TARGET_IDS:
        try:
            entity = await client.get_entity(chat_id)
            
            if isinstance(entity, Channel) and entity.megagroup:
                # Получаем полную информацию
                full = await client(GetFullChannelRequest(channel=entity))
                
                hidden = getattr(full.full_chat, 'hidden_prehistory', None)
                
                if hidden == False or hidden is None:
                    status = "✅"
                    history_status = "Открыта для новых участников"
                else:
                    status = "❌"
                    history_status = "Закрыта (только с момента добавления)"
                
                print(f"{status} {entity.title}")
                print(f"   hidden_prehistory: {hidden}")
                print(f"   Статус: {history_status}\n")
                
                results.append({
                    'name': entity.title,
                    'id': chat_id,
                    'hidden_prehistory': hidden,
                    'history_status': history_status
                })
            
        except Exception as e:
            print(f"⚠️ {chat_id}: {str(e)}\n")
            results.append({'id': chat_id, 'error': str(e)})
    
    with open('telegram_final_status.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    open_count = sum(1 for r in results if r.get('hidden_prehistory') in [False, None])
    
    print("=" * 60)
    print(f"✅ Супергруппы с открытой историей: {open_count}/{len(results)}")
    print("📄 Полный отчёт: telegram_final_status.json")

with client:
    client.loop.run_until_complete(final_check())
