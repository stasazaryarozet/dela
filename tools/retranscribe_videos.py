#!/usr/bin/env python3
"""
Перераспознавание видео через Yandex SpeechKit с максимальной точностью
Обновляет TRANSCRIPTS_ALL_VIDEOS.md
"""

import sys
from pathlib import Path
from datetime import datetime

# Добавляем пути
DELA_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(DELA_ROOT / "telegram-bot" / "tools"))

from yandex_speechkit import YandexSpeechKit

def main():
    project_dir = DELA_ROOT / "Ольга" / "Дизайн-путешествия" / "PARIS-2026"
    source_dir = project_dir / "source_materials"
    output_file = project_dir / "TRANSCRIPTS_ALL_VIDEOS.md"
    
    # Находим все видео
    videos = sorted(source_dir.glob("*bot_video*.mp4"))
    
    print(f"📂 Найдено видео: {len(videos)}")
    print(f"🎤 Движок: Yandex SpeechKit API v3 (general:rc - максимальная точность)")
    print()
    
    client = YandexSpeechKit()
    
    results = []
    total_chars = 0
    total_words = 0
    
    for i, video in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] {video.name}")
        
        try:
            result = client.transcribe(
                file_path=video,
                language="ru-RU",
                model="general:rc",
                literature_text=True,
                word_timestamps=True,
                cleanup_after=True
            )
            
            text = result.get('normalized_text') or result.get('text', '')
            words_count = len(result.get('words', []))
            chars_count = len(text)
            
            results.append({
                'filename': video.name,
                'text': text,
                'chars': chars_count,
                'words': words_count
            })
            
            total_chars += chars_count
            total_words += words_count
            
            print(f"   ✅ {chars_count} символов, {words_count} слов")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            results.append({
                'filename': video.name,
                'text': '',
                'chars': 0,
                'words': 0
            })
        
        print()
    
    # Формируем markdown
    content = f"""# ТРАНСКРИПТЫ ВСЕХ ВИДЕО ОТ БОТА

**Дата обработки:** {datetime.now().strftime("%d %B %Y, %H:%M")}
**Метод:** Yandex SpeechKit API v3 (general:rc - максимальная точность)
**Всего видео:** {len(videos)}

---

## 📊 СТАТИСТИКА

- Символов: {total_chars}
- Слов: {total_words}
- Среднее на видео: {total_chars // len(videos) if videos else 0} символов

---

## 📝 ТРАНСКРИПТЫ

"""
    
    for i, result in enumerate(results, 1):
        content += f"""### {i}. {result['filename']}

**Символов:** {result['chars']} | **Слов:** {result['words']}

{result['text']}

---

"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Транскрипты сохранены: {output_file}")
    print(f"📊 Итого: {total_chars} символов, {total_words} слов")


if __name__ == "__main__":
    main()

