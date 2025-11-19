#!/usr/bin/env python3
"""
Глубокая проверка: действительно ли история открыта
"""
from telethon.sync import TelegramClient
from telethon.tl.types import Channel
import json

with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']
client = TelegramClient('olga_session', olga['api_id'], olga['api_hash'])

async def deep_check():
    await client.start(phone=olga['phone'])
    
    print("🔍 Глубокая проверка супергрупп...\n")
    
    TARGET_IDS = [
        -1002688231781,  # ДЕЛАЕМ
        -1002434489044,  # Лето 25 - Современное искусство
        -1002616923445,  # Лето 25 - Колористика
        -1002399539099,  # Зима 25 - Колористика
        -1002293661920,  # Архитектура и дизайн XX-XXI века
    ]
    
    results = []
    for chat_id in TARGET_IDS:
        try:
            entity = await client.get_entity(chat_id)
            
            if isinstance(entity, Channel):
                # Получаем полную информацию о канале
                full = await client(functions.channels.GetFullChannelRequest(channel=entity))
                
                hidden_prehistory = getattr(full.full_chat, 'hidden_prehistory', None)
                
                status = "✅ Открыта" if hidden_prehistory == False else "❌ Закрыта"
                
                print(f"{status} {entity.title}")
                print(f"   hidden_prehistory: {hidden_prehistory}")
                
                results.append({
                    'name': entity.title,
                    'id': chat_id,
                    'hidden_prehistory': hidden_prehistory,
                    'history_visible': hidden_prehistory == False
                })
            
        except Exception as e:
            print(f"❌ {chat_id}: {str(e)}")
            results.append({'id': chat_id, 'error': str(e)})
        
        print()
    
    with open('telegram_history_deep_check.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("📄 Результаты: telegram_history_deep_check.json")

with client:
    client.loop.run_until_complete(deep_check())
