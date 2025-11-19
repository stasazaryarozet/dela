#!/usr/bin/env python3
"""
Полное извлечение информации об отелях включая media previews
"""
from telethon import TelegramClient
import json
import asyncio
import re
from collections import defaultdict

with open('telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient('olga_session', creds['api_id'], creds['api_hash'])

async def extract_complete():
    await client.start()
    
    print("🏨 Полное извлечение информации об отелях (включая media)...\n")
    
    paris_groups = [
        4906876993,  # ПАРИЖ сентябрь 25
        4180900155,  # ПАРИЖ СЕНТЯБРЬ 24
        4751416645,  # ПАРИЖ 25
        4587944253,  # Paris after tour
    ]
    
    hotel_keywords = [
        'отель', 'hotel', 'гостиниц', 'airbnb', 'booking',
        'жилье', 'accommodation', 'остановились', 'жили',
        'номер', 'room', 'квартира', 'apartment', 'hôtel',
        'рекоменд', 'recommend'
    ]
    
    hotels_complete = {
        'messages_with_media': [],
        'google_maps': [],
        'booking_links': [],
        'all_relevant': []
    }
    
    for group_id in paris_groups:
        try:
            entity = await client.get_entity(group_id)
            group_name = getattr(entity, 'title', f'Group {group_id}')
            print(f"📥 {group_name}")
            
            async for message in client.iter_messages(group_id, limit=None):
                text = message.text or ''
                text_lower = text.lower()
                
                msg_data = {
                    'id': message.id,
                    'date': message.date.isoformat() if message.date else None,
                    'text': text,
                    'group': group_name,
                    'sender_id': message.sender_id,
                    'media_type': None,
                    'media_data': {}
                }
                
                is_relevant = False
                
                # 1. Проверяем текст
                if any(kw in text_lower for kw in hotel_keywords):
                    is_relevant = True
                
                # 2. Проверяем media (КРИТИЧНО!)
                if message.media:
                    msg_data['media_type'] = type(message.media).__name__
                    
                    # WebPage preview (как Google Maps)
                    if hasattr(message.media, 'webpage'):
                        wp = message.media.webpage
                        msg_data['media_data'] = {
                            'type': 'webpage',
                            'url': getattr(wp, 'url', None),
                            'title': getattr(wp, 'title', None),
                            'description': getattr(wp, 'description', None),
                            'site_name': getattr(wp, 'site_name', None)
                        }
                        
                        # Проверяем title и description на релевантность
                        wp_text = f"{msg_data['media_data'].get('title', '')} {msg_data['media_data'].get('description', '')}".lower()
                        
                        if any(kw in wp_text for kw in hotel_keywords):
                            is_relevant = True
                        
                        # Google Maps
                        if 'google.com/maps' in text or (msg_data['media_data']['url'] and 'google.com/maps' in msg_data['media_data']['url']):
                            hotels_complete['google_maps'].append(msg_data)
                            is_relevant = True
                    
                    # Booking.com
                    if 'booking.com' in text_lower:
                        hotels_complete['booking_links'].append(msg_data)
                        is_relevant = True
                
                if is_relevant:
                    hotels_complete['all_relevant'].append(msg_data)
                    
                    # Получаем имя отправителя
                    try:
                        sender = await client.get_entity(message.sender_id)
                        msg_data['sender_name'] = f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip()
                    except:
                        msg_data['sender_name'] = 'Unknown'
            
            print(f"   ✅ Обработано")
            
        except Exception as e:
            print(f"   ⚠️ Ошибка: {e}")
    
    # Сохраняем
    with open('hotels_complete_data.json', 'w', encoding='utf-8') as f:
        json.dump(hotels_complete, f, indent=2, ensure_ascii=False, default=str)
    
    # Отчет
    print("\n" + "="*80)
    print("📊 ПОЛНЫЙ ОТЧЕТ")
    print("="*80)
    print(f"\n📍 Google Maps ссылки: {len(hotels_complete['google_maps'])}")
    for gm in hotels_complete['google_maps']:
        print(f"\n   [{gm['group']}] {gm['date'][:10] if gm['date'] else 'N/A'}")
        print(f"   От: {gm.get('sender_name', 'Unknown')}")
        if gm['media_data'].get('title'):
            print(f"   Название: {gm['media_data']['title']}")
        if gm['media_data'].get('url'):
            print(f"   🔗 {gm['media_data']['url']}")
        print(f"   Текст: {gm['text'][:150]}")
    
    print(f"\n🔗 Booking.com ссылки: {len(hotels_complete['booking_links'])}")
    
    print(f"\n📊 Всего релевантных сообщений: {len(hotels_complete['all_relevant'])}")
    print(f"   - С media: {sum(1 for m in hotels_complete['all_relevant'] if m['media_type'])}")
    print(f"   - Только текст: {sum(1 for m in hotels_complete['all_relevant'] if not m['media_type'])}")
    
    print("\n" + "="*80)
    print("💾 Полные данные: hotels_complete_data.json")
    print("="*80)
    
    await client.disconnect()
    return hotels_complete

if __name__ == '__main__':
    asyncio.run(extract_complete())
