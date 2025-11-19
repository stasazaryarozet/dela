#!/usr/bin/env python3
"""
МАКСИМАЛЬНАЯ интеграция: все возможные источники данных Telegram
"""
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogsRequest, SearchRequest, GetHistoryRequest
from telethon.tl.functions.contacts import SearchRequest as ContactsSearchRequest
from telethon.tl.types import InputPeerEmpty, InputMessagesFilterEmpty
import json
import asyncio

with open('telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient('olga_session', creds['api_id'], creds['api_hash'])

async def maximum_integration():
    await client.start()
    
    me = await client.get_me()
    print(f"🔐 Вошли как: {me.first_name} {me.last_name or ''}")
    print(f"    Телефон: {me.phone}")
    print(f"    Username: @{me.username if me.username else 'нет'}")
    print()
    
    print("="*80)
    print("МАКСИМАЛЬНАЯ ИНТЕГРАЦИЯ С TELEGRAM")
    print("="*80)
    
    # 1. Все диалоги (обычные + архив)
    print("\n1️⃣ Извлечение ВСЕХ диалогов...")
    
    all_dialogs = []
    
    # Обычные
    regular = await client.get_dialogs(limit=None, archived=False)
    all_dialogs.extend(regular)
    print(f"   Обычные: {len(regular)}")
    
    # Архивированные
    archived = await client.get_dialogs(limit=None, archived=True)
    all_dialogs.extend(archived)
    print(f"   Архивированные: {len(archived)}")
    
    # 2. Глобальный поиск по ключевым словам
    print("\n2️⃣ Глобальный поиск 'отели париж'...")
    
    search_results = []
    
    try:
        # Поиск по всем чатам
        result = await client(SearchRequest(
            peer=InputPeerEmpty(),
            q='отели париж',
            filter=InputMessagesFilterEmpty(),
            min_date=None,
            max_date=None,
            offset_id=0,
            add_offset=0,
            limit=100,
            max_id=0,
            min_id=0,
            hash=0
        ))
        
        for msg in result.messages:
            if msg.message:
                search_results.append({
                    'text': msg.message,
                    'date': msg.date.isoformat() if msg.date else None,
                    'chat_id': msg.peer_id
                })
        
        print(f"   Найдено: {len(search_results)} сообщений")
        
    except Exception as e:
        print(f"   ⚠️ Глобальный поиск недоступен: {e}")
    
    # 3. Поиск во ВСЕХ диалогах локально
    print("\n3️⃣ Локальный поиск 'рекомендованные отели' во ВСЕХ диалогах...")
    
    hotels_messages = []
    paris_chats = []
    
    for dialog in all_dialogs:
        entity = dialog.entity
        name = dialog.name
        
        # Фильтр: содержит 'париж' или 'paris'
        if 'париж' in name.lower() or 'paris' in name.lower():
            participants = getattr(entity, 'participants_count', 0)
            
            paris_chats.append({
                'name': name,
                'id': entity.id,
                'type': type(entity).__name__,
                'participants': participants,
                'archived': dialog.archived
            })
            
            print(f"\n   📍 {name}")
            print(f"      ID: {entity.id}")
            print(f"      Участников: {participants or 'N/A'}")
            print(f"      Архив: {dialog.archived}")
            
            # Ищем сообщения об отелях
            count = 0
            async for msg in client.iter_messages(entity, limit=None):
                if not msg.text:
                    continue
                
                text_lower = msg.text.lower()
                
                # Ключевые слова
                if any(kw in text_lower for kw in ['отел', 'hotel', 'рекоменд', 'google.com/maps']):
                    count += 1
                    
                    msg_data = {
                        'chat_name': name,
                        'chat_id': entity.id,
                        'msg_id': msg.id,
                        'date': msg.date.isoformat() if msg.date else None,
                        'text': msg.text,
                        'sender_id': msg.sender_id,
                        'media': None
                    }
                    
                    # Проверяем media
                    if msg.media and hasattr(msg.media, 'webpage'):
                        wp = msg.media.webpage
                        msg_data['media'] = {
                            'url': getattr(wp, 'url', None),
                            'title': getattr(wp, 'title', None),
                            'description': getattr(wp, 'description', None)
                        }
                        
                        # Это Google Maps с 17 отелями?
                        if msg_data['media']['title'] and '17 places' in msg_data['media']['title']:
                            print(f"\n      🎯 ЦЕЛЕВОЕ СООБЩЕНИЕ НАЙДЕНО!")
                            print(f"         Текст: {msg.text}")
                            print(f"         Title: {msg_data['media']['title']}")
                            print(f"         URL: {msg_data['media']['url']}")
                    
                    hotels_messages.append(msg_data)
            
            print(f"      ✅ Сообщений об отелях: {count}")
    
    print(f"\n   Итого Paris-чатов: {len(paris_chats)}")
    print(f"   Итого сообщений об отелях: {len(hotels_messages)}")
    
    # 4. Проверка контактов
    print("\n4️⃣ Поиск контакта 'Natalia Loginova'...")
    
    from telethon.tl.functions.contacts import GetContactsRequest
    result = await client(GetContactsRequest(hash=0))
    contacts = result.users
    natalia = None
    
    for contact in contacts:
        name = f"{contact.first_name} {contact.last_name or ''}".lower()
        if 'natalia' in name or 'наталия' in name or 'loginova' in name:
            print(f"   ✅ Найдено: {contact.first_name} {contact.last_name or ''}")
            print(f"      ID: {contact.id}")
            print(f"      Phone: {contact.phone if hasattr(contact, 'phone') else 'N/A'}")
            natalia = contact
    
    # 5. Сохранение всех данных
    print("\n5️⃣ Сохранение данных...")
    
    with open('telegram_maximum_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_dialogs': len(all_dialogs),
            'paris_chats': paris_chats,
            'hotels_messages': hotels_messages,
            'search_results': search_results,
            'natalia_contact': {
                'id': natalia.id if natalia else None,
                'name': f"{natalia.first_name} {natalia.last_name or ''}" if natalia else None
            }
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"   ✅ Сохранено: telegram_maximum_data.json")
    
    # Итоговый отчет
    print("\n" + "="*80)
    print("✅ МАКСИМАЛЬНАЯ ИНТЕГРАЦИЯ ЗАВЕРШЕНА")
    print("="*80)
    print(f"📊 Статистика:")
    print(f"   • Всего диалогов: {len(all_dialogs)}")
    print(f"   • Paris-чатов: {len(paris_chats)}")
    print(f"   • Сообщений об отелях: {len(hotels_messages)}")
    print(f"   • Результатов глобального поиска: {len(search_results)}")
    
    # Проверяем, нашли ли Google Maps с 17 отелями
    google_maps_17 = [m for m in hotels_messages if m['media'] and m['media'].get('title') and '17' in str(m['media']['title'])]
    
    if google_maps_17:
        print(f"\n🎯 НАЙДЕНА карта с 17 отелями:")
        for gm in google_maps_17:
            print(f"   Чат: {gm['chat_name']}")
            print(f"   URL: {gm['media']['url']}")
    else:
        print(f"\n⚠️ Карта Google Maps с 17 отелями НЕ НАЙДЕНА")
        print(f"   Возможные причины:")
        print(f"   • Сообщение в личном чате (не группе)")
        print(f"   • Сообщение удалено")
        print(f"   • Ограничение доступа API")
    
    print("="*80)
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(maximum_integration())
