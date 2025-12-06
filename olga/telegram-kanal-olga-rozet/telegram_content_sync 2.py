#!/usr/bin/env python3
"""
Telegram Content Gate: Автоматическая синхронизация контента с каналом @olgarozet

ПРИНЦИП: Единый источник истины (Single Source of Truth)
- Ольга редактирует .md файлы в Cursor
- Скрипт автоматически синхронизирует с Telegram
- Ноль ручных действий в Telegram UI

ЗАБОТА О ЧЕЛОВЕКЕ:
- Работа в привычном редакторе
- Версионирование (Git)
- Предпросмотр перед публикацией
- Возможность отката
"""

import os
import sys
import asyncio
import yaml
import json
from pathlib import Path
from datetime import datetime
from telethon import TelegramClient
import re

# Пути
PROJECT_ROOT = Path(__file__).parent
POSTS_DIR = PROJECT_ROOT / 'posts'
CHANNEL_CONFIG = PROJECT_ROOT / 'channel.yaml'
STATE_FILE = PROJECT_ROOT / '.sync_state.json'
GATES_PATH = Path('/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/.gates')

# Загружаем credentials
with open(GATES_PATH / 'telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient(str(GATES_PATH / 'olga_session'), creds['api_id'], creds['api_hash'])


def load_channel_config():
    """Загружает конфигурацию канала"""
    with open(CHANNEL_CONFIG, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_sync_state():
    """Загружает состояние синхронизации"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_sync_state(state):
    """Сохраняет состояние синхронизации"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def parse_post(file_path):
    """Парсит .md файл поста"""
    content = file_path.read_text(encoding='utf-8')
    
    # Извлекаем frontmatter (YAML между ---)
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError(f"Неверный формат файла: {file_path}")
    
    frontmatter = yaml.safe_load(match.group(1))
    text = match.group(2).strip()
    
    return {
        'metadata': frontmatter,
        'text': text,
        'file_path': file_path
    }


def update_post_metadata(file_path, updates):
    """Обновляет метаданные поста в файле"""
    post = parse_post(file_path)
    post['metadata'].update(updates)
    
    # Сериализуем обратно
    frontmatter_text = yaml.dump(post['metadata'], allow_unicode=True, sort_keys=False)
    new_content = f"---\n{frontmatter_text}---\n\n{post['text']}"
    
    file_path.write_text(new_content, encoding='utf-8')


async def sync_posts(preview_mode=False):
    """Синхронизирует посты с каналом"""
    await client.start()
    
    config = load_channel_config()
    state = load_sync_state()
    channel = await client.get_entity(config['channel']['username'])
    
    print("=" * 80)
    print(f"СИНХРОНИЗАЦИЯ: @{config['channel']['username']}")
    print("=" * 80)
    print()
    
    if preview_mode:
        print("⚠️ РЕЖИМ ПРЕДПРОСМОТРА (изменения не будут опубликованы)")
        print()
    
    # Собираем все посты
    post_files = sorted(POSTS_DIR.glob('*.md'))
    
    if not post_files:
        print("❌ Нет постов для синхронизации")
        await client.disconnect()
        return
    
    published_count = 0
    updated_count = 0
    skipped_count = 0
    
    for post_file in post_files:
        post = parse_post(post_file)
        post_id = post['metadata']['post_id']
        status = post['metadata'].get('status', 'draft')
        telegram_id = post['metadata'].get('telegram_id')
        pin = post['metadata'].get('pin', False)
        
        print(f"📄 {post_file.name} (ID: {post_id}, Status: {status})")
        
        # Пропускаем черновики
        if status == 'draft':
            print(f"   ⏸️ Черновик — пропущен")
            skipped_count += 1
            print()
            continue
        
        # Проверяем расписание
        if status == 'scheduled':
            schedule_time = datetime.fromisoformat(post['metadata'].get('schedule'))
            if datetime.now() < schedule_time:
                print(f"   ⏰ Запланирован на {schedule_time} — пропущен")
                skipped_count += 1
                print()
                continue
        
        # Публикация или обновление
        if telegram_id is None:
            # Новый пост
            if preview_mode:
                print(f"   📤 [PREVIEW] Будет опубликован:")
                print(f"      {post['text'][:100]}...")
            else:
                message = await client.send_message(channel, post['text'], link_preview=False)
                print(f"   ✅ Опубликован (Telegram ID: {message.id})")
                
                # Закрепляем, если нужно
                if pin:
                    await client.pin_message(channel, message)
                    print(f"   📌 Закреплён")
                
                # Обновляем metadata
                update_post_metadata(post_file, {
                    'telegram_id': message.id,
                    'status': 'published'
                })
                
                published_count += 1
        else:
            # Существующий пост — проверяем изменения
            current_hash = state.get(post_id, {}).get('hash')
            new_hash = hash(post['text'])
            
            if current_hash != new_hash:
                if preview_mode:
                    print(f"   ✏️ [PREVIEW] Будет обновлён (ID: {telegram_id})")
                else:
                    await client.edit_message(channel, telegram_id, post['text'], link_preview=False)
                    print(f"   ✅ Обновлён (Telegram ID: {telegram_id})")
                    
                    # Закрепляем/откр епляем
                    if pin:
                        await client.pin_message(channel, telegram_id)
                        print(f"   📌 Закреплён")
                    
                    updated_count += 1
                    
                # Обновляем хэш в state
                if post_id not in state:
                    state[post_id] = {}
                state[post_id]['hash'] = new_hash
            else:
                print(f"   ✓ Без изменений (Telegram ID: {telegram_id})")
                skipped_count += 1
        
        print()
    
    # Сохраняем состояние
    if not preview_mode:
        save_sync_state(state)
    
    print("=" * 80)
    print("ИТОГИ СИНХРОНИЗАЦИИ:")
    print("=" * 80)
    print()
    print(f"✅ Опубликовано: {published_count}")
    print(f"✏️ Обновлено: {updated_count}")
    print(f"⏸️ Пропущено: {skipped_count}")
    print()
    
    await client.disconnect()


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Синхронизация контента с Telegram-каналом @olgarozet',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Синхронизация (публикация изменений)
  python telegram_content_sync.py

  # Предпросмотр (без публикации)
  python telegram_content_sync.py --preview

  # Помощь
  python telegram_content_sync.py --help
        """
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Режим предпросмотра (не публикует изменения)'
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(sync_posts(preview_mode=args.preview))
    except KeyboardInterrupt:
        print("\n❌ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

