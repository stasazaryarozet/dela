#!/usr/bin/env python3
"""
ПОЛНАЯ интеграция с Telegram: все диалоги, включая скрытые/архивированные
"""
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import json
import asyncio

with open('telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient('olga_session', creds['api_id'], creds['api_hash'])

async def full_integration():
    await client.start()
    
    print("🔍 ПОЛНАЯ ИНТЕГРАЦИЯ: извлечение ВСЕХ диалогов...\n")
    
    all_entities = []
    
    # 1. Стандартные диалоги (включая архивированные)
    print("1️⃣ Получение всех диалогов (включая архив)...")
    
    dialogs = await client.get_dialogs(
        limit=None,
        archived=False  # Сначала не архивированные
    )
    
    for d in dialogs:
        all_entities.append({
            'id': d.entity.id,
            'name': d.name,
            'type': type(d.entity).__name__,
            'archived': False
        })
    
    print(f"   ✅ Найдено: {len(dialogs)} обычных диалогов")
    
    # 2. Архивированные диалоги
    print("\n2️⃣ Получение архивированных диалогов...")
    
    try:
        archived = await client.get_dialogs(
            limit=None,
            archived=True
        )
        
        for d in archived:
            all_entities.append({
                'id': d.entity.id,
                'name': d.name,
                'type': type(d.entity).__name__,
                'archived': True
            })
        
        print(f"   ✅ Найдено: {len(archived)} архивированных диалогов")
    except Exception as e:
        print(f"   ⚠️ Ошибка: {e}")
    
    # 3. Все чаты через GetAllChatsRequest
    print("\n3️⃣ Получение всех чатов через низкоуровневый API...")
    
    try:
        # Метод недоступен
        
        for chat in result.chats:
            if chat.id not in [e['id'] for e in all_entities]:
                all_entities.append({
                    'id': chat.id,
                    'name': getattr(chat, 'title', 'Unknown'),
                    'type': type(chat).__name__,
                    'archived': 'unknown'
                })
        
        print(f"   ✅ Дополнительно найдено: {len(result.chats)} чатов")
    except Exception as e:
        print(f"   ⚠️ Ошибка: {e}")
    
    # 4. Ищем конкретную группу "ПАРИЖ"
    print("\n4️⃣ Поиск группы 'ПАРИЖ' (2 участника)...")
    
    paris_groups = []
    for entity_info in all_entities:
        if 'париж' in entity_info['name'].lower():
            # Получаем детали
            try:
                entity = await client.get_entity(entity_info['id'])
                participants = getattr(entity, 'participants_count', None)
                
                paris_groups.append({
                    **entity_info,
                    'participants': participants
                })
                
                print(f"\n   📌 {entity_info['name']}")
                print(f"      ID: {entity_info['id']}")
                print(f"      Участников: {participants}")
                print(f"      Архивирована: {entity_info['archived']}")
                
                # Если 2 участника - это наша группа!
                if participants == 2:
                    print(f"\n   🎯 ЦЕЛЕВАЯ ГРУППА НАЙДЕНА!")
                    
                    # Извлекаем сообщение с отелями
                    print(f"\n   📥 Извлечение сообщений...")
                    
                    hotels_msg = None
                    async for msg in client.iter_messages(entity, limit=50):
                        if msg.text and 'рекомендованные отели' in msg.text.lower():
                            hotels_msg = {
                                'id': msg.id,
                                'date': msg.date.isoformat() if msg.date else None,
                                'text': msg.text,
                                'media': None
                            }
                            
                            if msg.media and hasattr(msg.media, 'webpage'):
                                wp = msg.media.webpage
                                hotels_msg['media'] = {
                                    'url': getattr(wp, 'url', None),
                                    'title': getattr(wp, 'title', None),
                                    'description': getattr(wp, 'description', None)
                                }
                            
                            print(f"\n   ✅ НАЙДЕНО СООБЩЕНИЕ:")
                            print(f"      Текст: {hotels_msg['text']}")
                            print(f"      Media URL: {hotels_msg['media']['url'] if hotels_msg['media'] else 'N/A'}")
                            print(f"      Media Title: {hotels_msg['media']['title'] if hotels_msg['media'] else 'N/A'}")
                            
                            # Сохраняем
                            with open('paris_hotels_google_maps.json', 'w', encoding='utf-8') as f:
                                json.dump(hotels_msg, f, indent=2, ensure_ascii=False)
                            
                            break
                    
                    if not hotels_msg:
                        print(f"\n   ⚠️ Сообщение 'рекомендованные отели' не найдено в последних 50")
                        
                        # Извлекаем ВСЕ сообщения
                        print(f"\n   📥 Извлечение ВСЕХ сообщений группы...")
                        all_msgs = []
                        async for msg in client.iter_messages(entity, limit=None):
                            if msg.text:
                                all_msgs.append({
                                    'id': msg.id,
                                    'date': msg.date.isoformat() if msg.date else None,
                                    'text': msg.text,
                                    'has_media': bool(msg.media)
                                })
                        
                        with open('paris_group_all_messages.json', 'w', encoding='utf-8') as f:
                            json.dump(all_msgs, f, indent=2, ensure_ascii=False)
                        
                        print(f"      ✅ Сохранено {len(all_msgs)} сообщений → paris_group_all_messages.json")
                
            except Exception as e:
                print(f"   ⚠️ Ошибка получения деталей: {e}")
    
    # Итоговый отчет
    print("\n" + "="*80)
    print(f"✅ ПОЛНАЯ ИНТЕГРАЦИЯ ЗАВЕРШЕНА")
    print("="*80)
    print(f"Всего уникальных диалогов: {len(all_entities)}")
    print(f"Групп 'Париж': {len(paris_groups)}")
    
    # Сохраняем все
    with open('telegram_full_map.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_entities': len(all_entities),
            'paris_groups': paris_groups,
            'all_entities': all_entities
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n�� Полная карта: telegram_full_map.json")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(full_integration())
