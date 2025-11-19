#!/usr/bin/env python3
"""
Авторизация Telegram аккаунта Азарьи (@stasazaryarozet)
"""
from telethon import TelegramClient
import json
import os

# Telegram API credentials
API_ID = 94575
API_HASH = 'a3406de8d171bb422bb6ddf3bbd800e2'

async def auth():
    print("📱 Авторизация Telegram аккаунта Азарьи")
    print()
    
    client = TelegramClient('azarya_session', API_ID, API_HASH)
    
    await client.start()
    
    print("✅ Авторизация успешна!")
    print()
    
    # Получаем информацию об аккаунте
    me = await client.get_me()
    print(f"👤 Имя: {me.first_name} {me.last_name or ''}")
    print(f"📞 Телефон: {me.phone}")
    print(f"🆔 User ID: {me.id}")
    print(f"📧 Username: @{me.username}" if me.username else "")
    print()
    
    # Сохраняем session string
    session_string = client.session.save()
    
    # Загружаем или создаем credentials
    credentials_path = 'telegram_credentials.json'
    
    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
    except FileNotFoundError:
        creds = {}
    
    creds['azarya'] = {
        'session': session_string,
        'api_id': API_ID,
        'api_hash': API_HASH,
        'user_id': me.id,
        'phone': me.phone,
        'username': me.username,
        'name': f"{me.first_name} {me.last_name or ''}".strip()
    }
    
    with open(credentials_path, 'w') as f:
        json.dump(creds, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Credentials сохранены: {credentials_path}")
    print()
    print("✅ Готово! Теперь ○ интегрирован с Telegram Азарьи")
    
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(auth())
