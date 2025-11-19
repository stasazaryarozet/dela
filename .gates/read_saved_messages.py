#!/usr/bin/env python3
"""
Чтение последнего сообщения из Saved Messages
"""
from telethon import TelegramClient
import json
import asyncio
import os
from datetime import datetime

# Определяем путь к корню проекта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
GATES_DIR = SCRIPT_DIR

async def read_saved_messages():
    # Загружаем credentials
    creds_path = os.path.join(GATES_DIR, 'telegram_credentials.json')
    with open(creds_path, 'r') as f:
        creds = json.load(f)['azarya']
    
    # Подключаемся к Telegram
    session_path = os.path.join(GATES_DIR, 'azarya_session')
    client = TelegramClient(session_path, creds['api_id'], creds['api_hash'])
    
    await client.start()
    
    print("📱 Подключено к Telegram")
    
    # Получаем информацию о себе
    me = await client.get_me()
    print(f"👤 Аккаунт: {me.first_name} {me.last_name or ''} (@{me.username or 'нет'})")
    print()
    
    # Saved Messages - это диалог с самим собой
    # Получаем диалог с собой
    saved_messages = await client.get_entity('me')
    
    print("📥 Читаю последнее сообщение из Saved Messages...")
    print()
    
    # Получаем последнее сообщение
    messages = await client.get_messages(saved_messages, limit=1)
    
    if messages and len(messages) > 0:
        last_message = messages[0]
        
        print("=" * 60)
        print("📨 ПОСЛЕДНЕЕ СООБЩЕНИЕ В SAVED MESSAGES")
        print("=" * 60)
        print()
        print(f"📅 Дата: {last_message.date.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("💬 Текст:")
        print("-" * 60)
        
        if last_message.message:
            print(last_message.message)
        else:
            print("(сообщение без текста)")
        
        print("-" * 60)
        print()
        
        # Проверяем наличие медиа
        if last_message.media:
            print(f"📎 Медиа: {type(last_message.media).__name__}")
        
        # Проверяем наличие вложений
        if last_message.entities:
            print(f"🔗 Сущности: {len(last_message.entities)}")
        
        print()
        print("=" * 60)
        
        # Возвращаем структурированные данные
        return {
            'date': last_message.date.isoformat(),
            'text': last_message.message or '',
            'has_media': last_message.media is not None,
            'media_type': type(last_message.media).__name__ if last_message.media else None,
            'message_id': last_message.id
        }
    else:
        print("❌ Saved Messages пусты")
        return None
    
    await client.disconnect()

if __name__ == '__main__':
    result = asyncio.run(read_saved_messages())
    if result:
        print()
        print("📋 JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

