#!/usr/bin/env python3
"""
Глубокий поиск групп Ольги по ключевым словам
"""
from telethon import TelegramClient
import json
import asyncio

with open('telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient('olga_session', creds['api_id'], creds['api_hash'])

async def deep_search():
    await client.start()
    
    print("🔍 Глубокий поиск групп Ольги...\n")
    
    # Ключевые слова
    keywords = [
        'розет', 'rozet', 'ольга', 'olga',
        'делаем', 'деlaem', 
        'париж', 'paris', 'january', 'январь',
        'вбшд', 'вбдш', 'школа дизайна',
        'путешеств', 'travel', 'тур',
        'фан', 'fan'
    ]
    
    dialogs = await client.get_dialogs()
    
    found_groups = []
    
    for dialog in dialogs:
        entity = dialog.entity
        
        # Только группы и супергруппы (не каналы)
        if not (hasattr(entity, 'megagroup') or (hasattr(entity, 'title') and not hasattr(entity, 'broadcast'))):
            continue
        
        title = getattr(entity, 'title', '').lower()
        username = getattr(entity, 'username', '') or ''
        username = username.lower()
        
        # Проверяем ключевые слова
        matched_keywords = []
        for keyword in keywords:
            if keyword in title or keyword in username:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            # Получаем детальную информацию
            try:
                full = await client.get_entity(entity.id)
                participants_count = getattr(full, 'participants_count', None)
                
                # Пытаемся получить описание
                description = ''
                if hasattr(full, 'about'):
                    description = full.about or ''
                
                info = {
                    'id': entity.id,
                    'title': getattr(entity, 'title', ''),
                    'username': getattr(entity, 'username', None),
                    'participants_count': participants_count,
                    'matched_keywords': matched_keywords,
                    'description': description[:200] if description else '',
                    'type': 'megagroup' if getattr(entity, 'megagroup', False) else 'group'
                }
                
                found_groups.append(info)
                
            except Exception as e:
                print(f"⚠️ Ошибка получения деталей для {getattr(entity, 'title', 'Unknown')}: {e}")
    
    # Сортируем по релевантности (количество совпадений)
    found_groups.sort(key=lambda x: len(x['matched_keywords']), reverse=True)
    
    print("=" * 80)
    print(f"🎯 НАЙДЕНО ГРУПП: {len(found_groups)}")
    print("=" * 80)
    
    for g in found_groups:
        print(f"\n{'='*80}")
        print(f"📌 {g['title']}")
        print(f"   Username: @{g['username']}" if g['username'] else "   Username: нет")
        print(f"   Участников: {g['participants_count']}" if g['participants_count'] else "   Участников: неизвестно")
        print(f"   Тип: {g['type']}")
        print(f"   Совпадения: {', '.join(g['matched_keywords'])}")
        if g['description']:
            print(f"   Описание: {g['description']}")
        print(f"   ID: {g['id']}")
    
    # Сохраняем
    with open('olga_groups_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(found_groups, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print(f"💾 Сохранено в olga_groups_filtered.json")
    print("=" * 80)
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(deep_search())
