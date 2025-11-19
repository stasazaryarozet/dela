#!/usr/bin/env python3
"""
Извлекает практические советы об отелях из Telegram групп Ольги
"""
from telethon.sync import TelegramClient
import json
import re

with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']
client = TelegramClient('olga_session', olga['api_id'], olga['api_hash'])

PARIS_GROUPS = [
    -4906876993,  # ПАРИЖ сентябрь 25
    -4180900155,  # ПАРИЖ СЕНТЯБРЬ 24
    -4751416645,  # ПАРИЖ 25
]

KEYWORDS = [
    'отель', 'hotel', 'район', 'arrondissement', 'метро', 
    'бюджет', 'цена', 'стоимость', 'завтрак', 'расположение',
    'близко', 'далеко', 'удобно', 'неудобно', 'рекомендую', 'советую'
]

async def extract_insights():
    await client.start(phone=olga['phone'])
    
    print("�� Извлекаю практические советы об отелях из групп Ольги...\n")
    
    all_insights = []
    
    for group_id in PARIS_GROUPS:
        try:
            entity = await client.get_entity(group_id)
            print(f"📍 {entity.title}...")
            
            messages = []
            async for msg in client.iter_messages(entity, limit=500):
                if msg.text:
                    text_lower = msg.text.lower()
                    if any(kw in text_lower for kw in KEYWORDS):
                        messages.append({
                            'date': msg.date.strftime('%Y-%m-%d'),
                            'text': msg.text,
                            'from': msg.sender_id
                        })
            
            print(f"   Найдено релевантных сообщений: {len(messages)}\n")
            
            all_insights.append({
                'group': entity.title,
                'messages': messages
            })
            
        except Exception as e:
            print(f"❌ {group_id}: {str(e)}\n")
    
    # Сохраняем
    with open('telegram_hotel_insights.json', 'w', encoding='utf-8') as f:
        json.dump(all_insights, f, indent=2, ensure_ascii=False)
    
    total = sum(len(g['messages']) for g in all_insights)
    print(f"✅ Извлечено сообщений: {total}")
    print("📄 Результаты: telegram_hotel_insights.json")

with client:
    client.loop.run_until_complete(extract_insights())
