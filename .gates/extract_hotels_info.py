#!/usr/bin/env python3
"""
Извлечение информации об отелях из всех групп Ольги
"""
from telethon import TelegramClient
import json
import asyncio
import re
from collections import defaultdict

with open('telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient('olga_session', creds['api_id'], creds['api_hash'])

async def extract_hotels():
    await client.start()
    
    print("🏨 Извлечение информации об отелях из Telegram Ольги...\n")
    
    # Группы Paris
    paris_groups = [
        4906876993,  # ПАРИЖ сентябрь 25
        4180900155,  # ПАРИЖ СЕНТЯБРЬ 24
        4751416645,  # ПАРИЖ 25
        4587944253,  # Paris after tour
    ]
    
    # Ключевые слова для поиска отелей
    hotel_keywords = [
        'отель', 'hotel', 'гостиниц', 'airbnb', 'booking',
        'жилье', 'accommodation', 'остановились', 'жили',
        'номер', 'room', 'квартира', 'apartment',
        'arrondissement', 'район', 'марэ', 'marais',
        'montmartre', 'монмартр', 'латинский', 'latin'
    ]
    
    hotels_data = {
        'recommendations': [],
        'experiences': [],
        'locations': defaultdict(list),
        'prices': [],
        'links': []
    }
    
    print("📥 Сканирование групп Paris...\n")
    
    for group_id in paris_groups:
        try:
            entity = await client.get_entity(group_id)
            group_name = getattr(entity, 'title', f'Group {group_id}')
            print(f"   Сканирую: {group_name}")
            
            message_count = 0
            async for message in client.iter_messages(group_id, limit=None):
                if not message.text:
                    continue
                
                text_lower = message.text.lower()
                
                # Проверяем релевантность
                is_relevant = any(keyword in text_lower for keyword in hotel_keywords)
                
                if is_relevant:
                    message_count += 1
                    
                    # Извлекаем ссылки
                    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)
                    
                    # Определяем тип информации
                    msg_data = {
                        'text': message.text,
                        'date': message.date.isoformat() if message.date else None,
                        'group': group_name,
                        'urls': urls
                    }
                    
                    # Классифицируем
                    if any(word in text_lower for word in ['рекоменд', 'советую', 'лучш', 'хорош', 'понравил']):
                        hotels_data['recommendations'].append(msg_data)
                    
                    if any(word in text_lower for word in ['останавливались', 'жили', 'был', 'ночевал']):
                        hotels_data['experiences'].append(msg_data)
                    
                    # Извлекаем районы
                    districts = re.findall(r'(\d{1,2})[- ]?(?:й|ый|ой|е)?\s*(?:округ|arrondissement|район)', text_lower)
                    for d in districts:
                        hotels_data['locations'][f"{d}-й округ"].append(msg_data)
                    
                    # Извлекаем цены
                    prices = re.findall(r'(\d+)\s*(?:евро|euro|€|eur)', text_lower)
                    if prices:
                        hotels_data['prices'].append({
                            'amount': prices[0],
                            'context': message.text[:200],
                            'date': message.date.isoformat() if message.date else None
                        })
                    
                    if urls:
                        hotels_data['links'].extend(urls)
            
            print(f"      ✅ Найдено сообщений: {message_count}")
            
        except Exception as e:
            print(f"      ⚠️ Ошибка: {e}")
    
    # Сохраняем сырые данные
    with open('hotels_raw_data.json', 'w', encoding='utf-8') as f:
        json.dump(hotels_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Генерируем структурированный отчет
    print("\n" + "="*80)
    print("📊 ОТЧЕТ: ИНФОРМАЦИЯ ОБ ОТЕЛЯХ В ПАРИЖЕ")
    print("="*80)
    
    print(f"\n📌 РЕКОМЕНДАЦИИ ({len(hotels_data['recommendations'])}):")
    for i, rec in enumerate(hotels_data['recommendations'][:10], 1):
        print(f"\n{i}. [{rec['group']}] {rec['date'][:10] if rec['date'] else 'N/A'}")
        print(f"   {rec['text'][:300]}")
        if rec['urls']:
            print(f"   🔗 {rec['urls'][0]}")
    
    print(f"\n🏠 ОПЫТ ПРОЖИВАНИЯ ({len(hotels_data['experiences'])}):")
    for i, exp in enumerate(hotels_data['experiences'][:10], 1):
        print(f"\n{i}. [{exp['group']}] {exp['date'][:10] if exp['date'] else 'N/A'}")
        print(f"   {exp['text'][:300]}")
    
    print(f"\n📍 ПО РАЙОНАМ:")
    for district, messages in sorted(hotels_data['locations'].items()):
        print(f"\n   {district}: {len(messages)} упоминаний")
        if messages:
            print(f"      Пример: {messages[0]['text'][:150]}")
    
    print(f"\n💰 ЦЕНЫ (примеры):")
    for price in hotels_data['prices'][:10]:
        print(f"   • {price['amount']}€ — {price['context'][:100]}")
    
    print(f"\n🔗 УНИКАЛЬНЫЕ ССЫЛКИ ({len(set(hotels_data['links']))}):")
    for url in sorted(set(hotels_data['links']))[:20]:
        print(f"   • {url}")
    
    print("\n" + "="*80)
    print(f"💾 Полные данные: hotels_raw_data.json")
    print("="*80)
    
    await client.disconnect()
    
    return hotels_data

if __name__ == '__main__':
    asyncio.run(extract_hotels())
