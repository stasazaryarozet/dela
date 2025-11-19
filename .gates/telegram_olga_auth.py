#!/usr/bin/env python3
"""
Авторизация Telegram аккаунта Ольги через Telethon (User API)
"""
from telethon import TelegramClient
from telethon.sessions import StringSession
import os

# Telegram API credentials (для User API, не Bot API)
API_ID = 94575  # Можно получить на my.telegram.org
API_HASH = 'a3406de8d171bb422bb6ddf3bbd800e2'  # Можно получить на my.telegram.org

async def auth():
    print("📱 Авторизация Telegram аккаунта Ольги")
    print()
    
    # Используем StringSession для хранения в файле
    client = TelegramClient('olga_session', API_ID, API_HASH)
    
    await client.start()
    
    print("✅ Авторизация успешна!")
    print()
    
    # Получаем информацию об аккаунте
    me = await client.get_me()
    print(f"👤 Имя: {me.first_name} {me.last_name or ''}")
    print(f"📞 Телефон: {me.phone}")
    print(f"🆔 User ID: {me.id}")
    print()
    
    # Сохраняем session string
    session_string = client.session.save()
    
    # Сохраняем в credentials
    credentials_path = os.path.join(os.path.dirname(__file__), 'telegram_credentials.json')
    import json
    
    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
    except FileNotFoundError:
        creds = {}
    
    creds['olga'] = {
        'session': session_string,
        'api_id': API_ID,
        'api_hash': API_HASH,
        'user_id': me.id,
        'phone': me.phone,
        'name': f"{me.first_name} {me.last_name or ''}".strip()
    }
    
    with open(credentials_path, 'w') as f:
        json.dump(creds, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Credentials сохранены: {credentials_path}")
    print()
    print("✅ Готово! Теперь можно использовать TelegramGate для Ольги")
    
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(auth())
