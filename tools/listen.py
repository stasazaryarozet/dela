#!/usr/bin/env python3
"""
LISTEN: ГОЛОСОВОЙ ИНТЕРФЕЙС ОПЕРАТОРА
Скрипт слушает папку inbox, транскрибирует голос и сохраняет смыслы.
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

# Добавляем текущую директорию в путь, чтобы импортировать соседние модули
sys.path.append(str(Path(__file__).parent))

try:
    from yandex_speechkit import YandexSpeechKit
except ImportError:
    print("❌ Ошибка: Не найден модуль yandex_speechkit.py")
    sys.exit(1)

# Конфигурация путей
BASE_DIR = Path(__file__).parent.parent / "olga" / "chelovek-i-remeslo-vsegda-i-seychas" / "recordings"
INBOX_DIR = BASE_DIR / "inbox"
AUDIO_DIR = BASE_DIR / "audio"
LOG_FILE = BASE_DIR / "VOICE_LOG.md"

def log_to_file(text, filename):
    """Добавляет запись в лог"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Создаем файл если нет
    if not LOG_FILE.exists():
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("# VOICE LOG\n\n")
            
    entry = f"\n## {timestamp} - {filename}\n\n{text}\n\n---\n"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)

def process_file(file_path):
    """Обрабатывает один аудиофайл"""
    print(f"\n🎤 Обнаружен голос: {file_path.name}")
    
    # 1. Перемещение в архив (Ingest)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"voice_{timestamp}_{file_path.name}"
    dest_path = AUDIO_DIR / new_filename
    
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file_path), str(dest_path))
    print(f"📦 Сохранен в архив: {new_filename}")
    
    # 2. Транскрипция
    print("🧠 Распознаю смысл...")
    try:
        stt = YandexSpeechKit()
        # Используем general:rc для лучшего качества
        result = stt.transcribe(
            file_path=dest_path,
            model="general:rc",
            literature_text=True,
            cleanup_after=True
        )
        
        text = result.get('normalized_text') or result.get('text', '')
        
        if text:
            print(f"\n💬 СМЫСЛ:\n{text}\n")
            log_to_file(text, new_filename)
            print(f"✅ Записано в {LOG_FILE.name}")
        else:
            print("⚠️  Текст не распознан (тишина?)")
            
    except Exception as e:
        print(f"❌ Ошибка распознавания: {e}")
        log_to_file(f"ERROR: {e}", new_filename)

def listen_loop():
    """Бесконечный цикл прослушивания"""
    print(f"👂 Слушаю папку: {INBOX_DIR}")
    print("   (Нажмите Ctrl+C для остановки)")
    
    # Создаем inbox если нет
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        while True:
            # Сканируем файлы
            files = [f for f in INBOX_DIR.iterdir() if f.is_file() and f.name != '.DS_Store']
            
            # Сортируем по времени создания (старые первыми)
            files.sort(key=lambda f: f.stat().st_mtime)
            
            for file_path in files:
                # Игнорируем временные файлы
                if file_path.name.startswith('.'):
                    continue
                    
                process_file(file_path)
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Прослушивание остановлено.")

if __name__ == "__main__":
    listen_loop()
