#!/usr/bin/env python3
"""
Обработка группы "Париж 2025" из Telegram.

Архитектурное решение для полной обработки содержания группы:
1. Чтение истории через TelegramGroupGate
2. Экспорт в Substance формат
3. Сохранение в структурированном виде
4. Интеграция с существующей архитектурой Gates
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Добавляем путь к gates
gates_dir = Path(__file__).parent
sys.path.insert(0, str(gates_dir))

from telegram_group_gate import TelegramGroupGate


# === КОНФИГУРАЦИЯ ===

GROUP_NAME = "ПАРИЖ сентябрь 25"  # Имя группы в Telegram
OUTPUT_DIR = Path(__file__).parent.parent / "Ольга" / "Дизайн-путешествия" / "PARIS-2026" / "telegram_group"
SUBSTANCE_DIR = gates_dir.parent / ".substance"  # Централизованное хранилище Substance


async def process_group():
    """Полная обработка группы Париж 2025"""
    
    print("=" * 80)
    print("ОБРАБОТКА ГРУППЫ 'ПАРИЖ 2025'")
    print("=" * 80)
    print()
    
    # Инициализация Gate
    try:
        gate = TelegramGroupGate()
        print("✅ Telegram Group Gate инициализирован")
    except ValueError as e:
        print(f"❌ Ошибка инициализации: {e}")
        print("\nТребуются переменные окружения:")
        print("  export TELEGRAM_API_ID='...'")
        print("  export TELEGRAM_API_HASH='...'")
        print("  export TELEGRAM_PHONE='+7...'")
        return
    
    # Проверка подключения
    print("\n🔐 Проверка подключения...")
    try:
        connection = await gate.test_connection()
        print(f"✓ Подключен как: {connection['user']}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    # Информация о группе
    print(f"\n📊 Поиск группы '{GROUP_NAME}'...")
    try:
        chat_info = await gate.get_chat_info(GROUP_NAME)
        print(f"✓ Группа найдена: {chat_info['title']}")
        print(f"  ID: {chat_info['id']}")
        print(f"  Тип: {chat_info['type']}")
        if 'member_count' in chat_info:
            print(f"  Участников: {chat_info['member_count']}")
    except ValueError as e:
        print(f"❌ Группа не найдена: {e}")
        print("\nВозможные причины:")
        print("  1. Группа называется по-другому")
        print("  2. Вы не являетесь участником группы")
        print("  3. Используйте точное имя или username (@groupname)")
        return
    
    # Чтение всех сообщений
    print(f"\n📬 Чтение истории группы (лимит: 1000 сообщений)...")
    try:
        messages = await gate.read_messages(GROUP_NAME, limit=1000)
        print(f"✓ Прочитано сообщений: {len(messages)}")
    except Exception as e:
        print(f"❌ Ошибка чтения сообщений: {e}")
        return
    
    # Получение участников
    print(f"\n👥 Получение списка участников...")
    try:
        members = await gate.get_group_members(GROUP_NAME)
        print(f"✓ Участников: {len(members)}")
    except Exception as e:
        print(f"⚠️  Не удалось получить участников: {e}")
        members = []
    
    # Экспорт Substance
    print(f"\n📦 Экспорт Substance...")
    try:
        substance = await gate.export_substance(
            GROUP_NAME,
            messages_limit=1000,
            include_members=True
        )
        print(f"✓ Substance экспортирован")
        print(f"  Сообщений: {substance['statistics']['total_messages']}")
        print(f"  Участников: {substance['statistics']['total_members']}")
        print(f"  С медиа: {substance['statistics']['messages_with_media']}")
        print(f"  С текстом: {substance['statistics']['messages_with_text']}")
        
        if substance['statistics']['date_range']:
            date_range = substance['statistics']['date_range']
            print(f"  Период: {date_range['oldest']} — {date_range['newest']}")
    except Exception as e:
        print(f"❌ Ошибка экспорта: {e}")
        return
    
    # Сохранение результатов
    print(f"\n💾 Сохранение результатов...")
    
    # Создаем директории
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUBSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Полный Substance (JSON)
    substance_file = SUBSTANCE_DIR / f"telegram_paris2025_{timestamp}.json"
    with open(substance_file, 'w', encoding='utf-8') as f:
        json.dump(substance, f, ensure_ascii=False, indent=2)
    print(f"✓ Substance: {substance_file}")
    
    # 2. Только сообщения (для удобства)
    messages_file = OUTPUT_DIR / f"messages_{timestamp}.json"
    with open(messages_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print(f"✓ Сообщения: {messages_file}")
    
    # 3. Участники
    if members:
        members_file = OUTPUT_DIR / f"members_{timestamp}.json"
        with open(members_file, 'w', encoding='utf-8') as f:
            json.dump(members, f, ensure_ascii=False, indent=2)
        print(f"✓ Участники: {members_file}")
    
    # 4. Текстовый дамп (для чтения)
    text_dump_file = OUTPUT_DIR / f"dump_{timestamp}.txt"
    with open(text_dump_file, 'w', encoding='utf-8') as f:
        f.write(f"Группа: {chat_info['title']}\n")
        f.write(f"ID: {chat_info['id']}\n")
        f.write(f"Экспорт: {datetime.now().isoformat()}\n")
        f.write("=" * 80 + "\n\n")
        
        for msg in messages:
            user = msg.get('from_user', {})
            user_name = user.get('first_name', 'Unknown') if user else 'Unknown'
            if user.get('username'):
                user_name += f" (@{user['username']})"
            
            date_str = msg.get('date', 'N/A')
            text = msg.get('text', '')
            
            f.write(f"[{date_str}] {user_name}:\n")
            if text:
                f.write(f"{text}\n")
            if msg.get('media'):
                f.write(f"[{msg['media']['type']}]\n")
            f.write("\n")
    
    print(f"✓ Текстовый дамп: {text_dump_file}")
    
    # 5. Статистика
    stats_file = OUTPUT_DIR / f"statistics_{timestamp}.json"
    stats = {
        'export_date': datetime.now(timezone.utc).isoformat(),
        'chat': chat_info,
        'statistics': substance['statistics'],
        'files': {
            'substance': str(substance_file),
            'messages': str(messages_file),
            'members': str(members_file) if members else None,
            'text_dump': str(text_dump_file)
        }
    }
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✓ Статистика: {stats_file}")
    
    # Закрытие соединения
    await gate.close()
    
    print("\n" + "=" * 80)
    print("✅ ОБРАБОТКА ЗАВЕРШЕНА")
    print("=" * 80)
    print(f"\n📁 Результаты сохранены в: {OUTPUT_DIR}")
    print(f"📦 Substance: {substance_file}")
    print(f"\n📊 Статистика:")
    print(f"  Сообщений: {substance['statistics']['total_messages']}")
    print(f"  Участников: {substance['statistics']['total_members']}")
    print(f"  С медиа: {substance['statistics']['messages_with_media']}")
    print(f"  С текстом: {substance['statistics']['messages_with_text']}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(process_group())

