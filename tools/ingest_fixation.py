#!/usr/bin/env python3
"""
INGEST FIXATION: ЗАБОТА О ДАННЫХ
Скрипт бережно принимает файлы от человека и раскладывает их по местам.

Принципы:
1. Не требовать от человека правильных имен файлов.
2. Не требовать от человека сортировки.
3. Сохранять всё, ничего не удалять без спроса.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def log(msg):
    print(f"🤍 {msg}")

def ingest_with_care(event_id):
    base_path = Path('olga/chelovek-i-remeslo-vsegda-i-seychas/recordings')
    inbox = base_path / 'inbox'
    
    if not inbox.exists() or not any(inbox.iterdir()):
        log(f"Папка {inbox} пуста. Жду файлов от человека...")
        return

    log(f"Начинаю бережную обработку события: {event_id}")
    
    # Создаем структуру, если нет
    (base_path / 'audio').mkdir(exist_ok=True)
    (base_path / 'video').mkdir(exist_ok=True)
    
    count = 0
    for file_path in inbox.iterdir():
        if file_path.name == '.DS_Store': continue
        
        # Определяем тип с любовью к форматам
        suffix = file_path.suffix.lower()
        is_video = suffix in ['.mp4', '.mov', '.avi', '.m4v']
        
        target_dir = base_path / ('video' if is_video else 'audio')
        
        # Формируем понятное имя, сохраняя оригинал
        timestamp = datetime.now().strftime("%H%M")
        clean_name = f"{event_id}_{timestamp}_{file_path.name}"
        destination = target_dir / clean_name
        
        log(f"📦 Бережно переношу: {file_path.name} -> {destination}")
        shutil.move(str(file_path), str(destination))
        count += 1
        
    log(f"✨ Готово. Обработано файлов: {count}. Спасибо!")

if __name__ == "__main__":
    # По умолчанию - ближайшее событие
    ingest_with_care("2025-12-02_cdl")
