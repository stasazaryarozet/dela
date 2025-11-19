#!/usr/bin/env python3
"""
Исследование Telegram Ольги: все группы, каналы, чаты
"""
from telethon import TelegramClient
import json
import asyncio

# Загружаем credentials
with open('telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient('olga_session', creds['api_id'], creds['api_hash'])

async def explore():
    await client.start()
    
    print("🔍 Исследую Telegram Ольги...\n")
    
    # Получаем все диалоги (группы, каналы, личные чаты)
    dialogs = await client.get_dialogs()
    
    groups = []
    channels = []
    personal = []
    
    for dialog in dialogs:
        entity = dialog.entity
        
        info = {
            'id': entity.id,
            'title': getattr(entity, 'title', None) or getattr(entity, 'first_name', 'Unknown'),
            'username': getattr(entity, 'username', None),
            'participants_count': getattr(entity, 'participants_count', None),
            'type': type(entity).__name__
        }
        
        # Классифицируем
        if hasattr(entity, 'megagroup') and entity.megagroup:
            groups.append(info)
        elif hasattr(entity, 'broadcast') and entity.broadcast:
            channels.append(info)
        elif hasattr(entity, 'title'):  # Обычная группа
            groups.append(info)
        else:
            personal.append(info)
    
    # Выводим группы
    print("=" * 60)
    print(f"👥 ГРУППЫ ({len(groups)}):")
    print("=" * 60)
    for g in groups:
        username_str = f"@{g['username']}" if g['username'] else "без username"
        participants = f"({g['participants_count']} участников)" if g['participants_count'] else ""
        print(f"\n📌 {g['title']}")
        print(f"   {username_str} {participants}")
        print(f"   ID: {g['id']}")
    
    # Выводим каналы
    print("\n" + "=" * 60)
    print(f"📢 КАНАЛЫ ({len(channels)}):")
    print("=" * 60)
    for c in channels:
        username_str = f"@{c['username']}" if c['username'] else "без username"
        participants = f"({c['participants_count']} подписчиков)" if c['participants_count'] else ""
        print(f"\n📌 {c['title']}")
        print(f"   {username_str} {participants}")
        print(f"   ID: {c['id']}")
    
    # Сохраняем в файл
    output = {
        'groups': groups,
        'channels': channels,
        'personal_chats_count': len(personal),
        'total_dialogs': len(dialogs)
    }
    
    with open('olga_telegram_map.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"💾 Сохранено в olga_telegram_map.json")
    print(f"📊 Всего диалогов: {len(dialogs)}")
    print(f"   - Группы: {len(groups)}")
    print(f"   - Каналы: {len(channels)}")
    print(f"   - Личные чаты: {len(personal)}")
    print("=" * 60)
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(explore())
