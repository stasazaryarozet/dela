#!/usr/bin/env python3
"""
Telegram Content Sync — Синхронизация контента с каналом @olgarozet

Читает UNIVERSAL_CONTENT.md и публикует изменения в Telegram
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import hashlib

# Относительные пути
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONTENT_SOURCE = PROJECT_ROOT / 'olga' / 'olgaroset.ru' / 'UNIFIED_CONTENT.md'
SYNC_STATE = Path(__file__).parent / '.sync_state.json'

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def get_content_hash(filepath):
    """Вычислить хеш содержимого файла"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_sync_state():
    """Загрузить состояние последней синхронизации"""
    if SYNC_STATE.exists():
        with open(SYNC_STATE, 'r') as f:
            return json.load(f)
    return {}

def save_sync_state(state):
    """Сохранить состояние синхронизации"""
    with open(SYNC_STATE, 'w') as f:
        json.dump(state, f, indent=2)

def sync():
    log("🔄 Проверка изменений в UNIVERSAL_CONTENT.md...")
    
    if not CONTENT_SOURCE.exists():
        log(f"❌ {CONTENT_SOURCE} не найден")
        return False
    
    # Вычислить хеш текущего контента
    current_hash = get_content_hash(CONTENT_SOURCE)
    
    # Загрузить предыдущее состояние
    state = load_sync_state()
    last_hash = state.get('content_hash')
    
    if current_hash == last_hash:
        log("✅ Контент не изменился, синхронизация не требуется")
        return True
    
    log("📝 Обнаружены изменения, синхронизация с Telegram...")
    
    # Публикация в Telegram через Telethon (User API)
    try:
        # Читаем контент
        with open(CONTENT_SOURCE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим контент для Telegram (берем первые 4096 символов)
        # Telegram имеет лимит на длину сообщения
        telegram_content = content[:4000]
        
        # Импортируем Telethon
        from telethon import TelegramClient
        
        # Credentials из telegram_olga_auth.py
        API_ID = 94575
        API_HASH = 'a3406de8d171bb422bb6ddf3bbd800e2'
        
        # Путь к сессии
        session_path = Path(__file__).parent / 'anon.session'
        
        # Создаем клиент
        client = TelegramClient(str(session_path), API_ID, API_HASH)
        
        async def post_to_channel():
            await client.connect()
            if not await client.is_user_authorized():
                log("❌ Сессия не авторизована. Запустите telegram_olga_auth.py")
                return False
            
            # Публикуем в канал @olgarozet
            await client.send_message('@olgarozet', telegram_content)
            log("✅ Опубликовано в @olgarozet")
            await client.disconnect()
            return True
        
        # Запускаем асинхронную публикацию
        import asyncio
        success = asyncio.run(post_to_channel())
        
        if not success:
            log("⚠️ Публикация не удалась")
            return False
            
    except ImportError:
        log("❌ Telethon не установлен: pip install telethon")
        return False
    except Exception as e:
        log(f"❌ Ошибка публикации: {e}")
        return False
    
    # Обновить состояние
    state['content_hash'] = current_hash
    state['last_sync'] = datetime.now().isoformat()
    state['sync_status'] = 'simulated'  # Пока не реализовано
    save_sync_state(state)
    
    log("✅ Состояние синхронизации обновлено")
    return True

if __name__ == '__main__':
    try:
        success = sync()
        sys.exit(0 if success else 1)
    except Exception as e:
        log(f"❌ Ошибка: {e}")
        sys.exit(1)




