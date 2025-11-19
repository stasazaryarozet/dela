#!/usr/bin/env python3
"""
CLEANUP YANDEX OBJECT STORAGE BUCKET
Скрипт для ручной очистки бакета и проверки его состояния
"""

import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / 'telegram-bot' / 'tools'))

from yandex_object_storage import YandexObjectStorage


def check_bucket_status():
    """Проверяет текущее состояние бакета"""
    storage = YandexObjectStorage()
    
    print("\n" + "="*70)
    print("🪣 СОСТОЯНИЕ YANDEX OBJECT STORAGE BUCKET")
    print("="*70)
    
    files = storage.list_files()
    
    if not files:
        print("\n✅ БАКЕТ ПУСТ")
        print("   Все временные файлы удалены корректно.")
        return True
    
    print(f"\n⚠️  НАЙДЕНО ФАЙЛОВ: {len(files)}")
    print("\nСписок файлов:")
    
    for i, f in enumerate(files, 1):
        print(f"   {i}. {f}")
    
    return False


def cleanup_all():
    """Удаляет ВСЕ файлы из бакета"""
    storage = YandexObjectStorage()
    
    files = storage.list_files()
    
    if not files:
        print("\n✅ Бакет уже пуст")
        return
    
    print(f"\n🗑️  Удаляю {len(files)} файлов...")
    
    for f in files:
        try:
            storage.delete_file(f)
        except Exception as e:
            print(f"   ⚠️  Не удалось удалить {f}: {e}")
    
    # Проверка
    remaining = storage.list_files()
    if not remaining:
        print(f"\n✅ Все файлы удалены. Бакет пуст.")
    else:
        print(f"\n⚠️  Остались файлы: {len(remaining)}")


def cleanup_old(hours: int = 1):
    """Удаляет файлы старше N часов"""
    storage = YandexObjectStorage()
    storage.cleanup_old_files(max_age_hours=hours)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Очистка Yandex Object Storage')
    parser.add_argument('--check', action='store_true', 
                       help='Проверить состояние бакета')
    parser.add_argument('--cleanup-all', action='store_true',
                       help='Удалить ВСЕ файлы')
    parser.add_argument('--cleanup-old', type=int, metavar='HOURS',
                       help='Удалить файлы старше N часов')
    
    args = parser.parse_args()
    
    if args.check:
        is_empty = check_bucket_status()
        sys.exit(0 if is_empty else 1)
    
    elif args.cleanup_all:
        print("\n⚠️  ВЫ СОБИРАЕТЕСЬ УДАЛИТЬ ВСЕ ФАЙЛЫ ИЗ БАКЕТА")
        confirm = input("Продолжить? [y/N]: ")
        if confirm.lower() == 'y':
            cleanup_all()
    
    elif args.cleanup_old:
        cleanup_old(hours=args.cleanup_old)
    
    else:
        # По умолчанию — просто проверка
        check_bucket_status()
