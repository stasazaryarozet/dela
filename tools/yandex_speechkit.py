#!/usr/bin/env python3
"""
YANDEX SPEECHKIT API V3 - УНИВЕРСАЛЬНЫЙ МОДУЛЬ

Асинхронное распознавание аудио/видео с максимальной точностью для русского языка.

Архитектура:
1. Загрузка файла на Yandex Object Storage (временно)
2. Отправка запроса на распознавание через API v3
3. Ожидание результата (polling)
4. Получение транскрипта с временными метками
5. Очистка временного файла

Требования:
- Сервисный аккаунт Yandex Cloud с ролями:
  * storage.uploader
  * ai.speechkit-stt.user
- API key или IAM token

Использование:
    from yandex_speechkit import YandexSpeechKit
    
    stt = YandexSpeechKit(api_key="YOUR_API_KEY")
    result = stt.transcribe("video.mp4", language="ru-RU")
    print(result['text'])
"""

import os
import time
import json
import requests
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class YandexSpeechKit:
    """Клиент для работы с Yandex SpeechKit API v3"""
    
    # API endpoints
    STT_ASYNC_URL = "https://stt.api.cloud.yandex.net:443/stt/v3/recognizeFileAsync"
    OPERATION_URL = "https://operation.api.cloud.yandex.net/operations"
    RECOGNITION_URL = "https://stt.api.cloud.yandex.net:443/stt/v3/getRecognition"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        iam_token: Optional[str] = None,
        folder_id: Optional[str] = None
    ):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ сервисного аккаунта (приоритет)
            iam_token: IAM токен (альтернатива API ключу)
            folder_id: ID каталога Yandex Cloud (опционально)
        """
        self.api_key = api_key or os.getenv('YANDEX_SPEECHKIT_API_KEY')
        self.iam_token = iam_token or os.getenv('YANDEX_IAM_TOKEN')
        self.folder_id = folder_id or os.getenv('YANDEX_FOLDER_ID')
        
        if not self.api_key and not self.iam_token:
            raise ValueError(
                "Требуется API key или IAM token. "
                "Установите переменные окружения: "
                "YANDEX_SPEECHKIT_API_KEY или YANDEX_IAM_TOKEN"
            )
    
    def _get_auth_header(self) -> Dict[str, str]:
        """Формирует заголовок авторизации"""
        if self.api_key:
            return {"Authorization": f"Api-Key {self.api_key}"}
        return {"Authorization": f"Bearer {self.iam_token}"}
    
    def _upload_to_object_storage(self, file_path: Path) -> str:
        """
        Загружает файл в Yandex Object Storage через yc CLI
        
        Args:
            file_path: Путь к локальному файлу
            
        Returns:
            Публичная ссылка на файл в Object Storage
        """
        try:
            from yandex_object_storage import YandexObjectStorage
            
            storage = YandexObjectStorage()
            public_url = storage.upload_file(file_path)
            
            return public_url
            
        except ImportError:
            raise ImportError(
                "Модуль yandex_object_storage не найден. "
                "Убедитесь, что tools/yandex_object_storage.py существует"
            )
        except Exception as e:
            raise RuntimeError(
                f"Не удалось загрузить файл в Object Storage: {e}\n\n"
                f"Альтернатива: загрузите файл вручную и используйте "
                f"transcribe_from_uri(uri)"
            )
    
    def transcribe(
        self,
        file_path: Path | str,
        language: str = "ru-RU",
        model: str = "general",
        audio_format: str = "AUTO",
        profanity_filter: bool = False,
        literature_text: bool = True,
        speaker_labeling: bool = False,
        word_timestamps: bool = True,
        cleanup_after: bool = True
    ) -> Dict:
        """
        Транскрибирует локальный файл (автоматически загружает в Object Storage)
        
        Args:
            file_path: Путь к локальному аудио/видео файлу
            language: Язык распознавания (ru-RU, en-US, etc.)
            model: Модель распознавания
            audio_format: Формат аудио (AUTO автоопределит)
            profanity_filter: Фильтр мата
            literature_text: Литературный текст (пунктуация, заглавные)
            speaker_labeling: Метки спикеров
            word_timestamps: Временные метки слов
            cleanup_after: Удалить файл из Object Storage после транскрипции
            
        Returns:
            Словарь с результатами распознавания
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        print(f"🎬 Транскрипция локального файла: {file_path.name}")
        
        # 1. Загружаем в Object Storage
        uri = self._upload_to_object_storage(file_path)
        
        # 2. Транскрибируем
        try:
            result = self.transcribe_from_uri(
                uri=uri,
                language=language,
                model=model,
                audio_format=audio_format,
                profanity_filter=profanity_filter,
                literature_text=literature_text,
                speaker_labeling=speaker_labeling,
                word_timestamps=word_timestamps
            )
            
            # 3. Очищаем (опционально)
            if cleanup_after:
                try:
                    from yandex_object_storage import YandexObjectStorage
                    storage = YandexObjectStorage()
                    
                    # Извлекаем имя объекта из URI
                    object_name = uri.split(storage.bucket_name + '/')[-1]
                    storage.delete_file(object_name)
                    
                except Exception as e:
                    print(f"⚠️  Не удалось удалить временный файл: {e}")
            
            return result
            
        except Exception as e:
            # В случае ошибки всё равно пытаемся удалить временный файл
            if cleanup_after:
                try:
                    from yandex_object_storage import YandexObjectStorage
                    storage = YandexObjectStorage()
                    object_name = uri.split(storage.bucket_name + '/')[-1]
                    storage.delete_file(object_name)
                except:
                    pass
            raise
    
    def transcribe_from_uri(
        self,
        uri: str,
        language: str = "ru-RU",
        model: str = "general",
        audio_format: str = "AUTO",
        profanity_filter: bool = False,
        literature_text: bool = True,
        speaker_labeling: bool = False,
        word_timestamps: bool = True
    ) -> Dict:
        """
        Распознает аудио/видео по ссылке в Object Storage
        
        Args:
            uri: Ссылка на файл в Yandex Object Storage
            language: Язык распознавания (ru-RU, en-US, etc.)
            model: Модель распознавания (general, general:rc, etc.)
            audio_format: Формат аудио (AUTO, WAV, MP3, OGG_OPUS, etc.)
            profanity_filter: Фильтр мата
            literature_text: Литературный текст (пунктуация, заглавные буквы)
            speaker_labeling: Метки спикеров
            word_timestamps: Временные метки слов
            
        Returns:
            Словарь с результатами распознавания
        """
        # 1. Формируем запрос на распознавание
        request_body = {
            "uri": uri,
            "recognition_model": {
                "model": model,
                "audio_format": {
                    "container_audio": {
                        "container_audio_type": audio_format
                    }
                },
                "text_normalization": {
                    "text_normalization": "TEXT_NORMALIZATION_ENABLED",
                    "profanity_filter": profanity_filter,
                    "literature_text": literature_text
                },
                "language_restriction": {
                    "restriction_type": "WHITELIST",
                    "language_code": [language]
                },
                "audio_processing_type": "FULL_DATA"
            }
        }
        
        # Опциональные параметры
        if speaker_labeling:
            request_body["recognition_model"]["speaker_labeling"] = {
                "speaker_labeling": "SPEAKER_LABELING_ENABLED"
            }
        
        print(f"📤 Отправка запроса на распознавание...")
        print(f"   Язык: {language}")
        print(f"   Модель: {model}")
        print(f"   Формат: {audio_format}")
        
        # 2. Отправляем запрос
        response = requests.post(
            self.STT_ASYNC_URL,
            headers={
                **self._get_auth_header(),
                "Content-Type": "application/json"
            },
            json=request_body,
            verify=True
        )
        
        if response.status_code != 200:
            raise Exception(
                f"Ошибка запроса распознавания: {response.status_code}\n"
                f"{response.text}"
            )
        
        operation = response.json()
        operation_id = operation['id']
        print(f"✅ Операция создана: {operation_id}")
        
        # 3. Ожидаем завершения (polling)
        print(f"⏳ Ожидание завершения распознавания...")
        
        max_attempts = 120  # 10 минут (5 сек * 120)
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(5)
            attempt += 1
            
            # Проверяем статус операции
            status_response = requests.get(
                f"{self.OPERATION_URL}/{operation_id}",
                headers=self._get_auth_header(),
                verify=True
            )
            
            if status_response.status_code != 200:
                raise Exception(
                    f"Ошибка проверки статуса: {status_response.status_code}\n"
                    f"{status_response.text}"
                )
            
            status = status_response.json()
            
            if status.get('done'):
                print(f"✅ Распознавание завершено!")
                break
            
            if attempt % 6 == 0:  # Каждые 30 секунд
                print(f"   Ожидание... ({attempt * 5}с)")
        
        if not status.get('done'):
            raise Exception("Timeout: распознавание не завершилось за 10 минут")
        
        # 4. Получаем результаты
        print(f"📥 Получение результатов...")
        
        result_response = requests.get(
            self.RECOGNITION_URL,
            headers=self._get_auth_header(),
            params={"operation_id": operation_id},
            verify=True
        )
        
        if result_response.status_code != 200:
            raise Exception(
                f"Ошибка получения результатов: {result_response.status_code}\n"
                f"{result_response.text}"
            )
        
        # 5. Парсим результаты
        raw_results = result_response.text
        results = self._parse_recognition_results(raw_results)
        
        print(f"✅ Распознано: {len(results['text'])} символов")
        
        return results
    
    def _parse_recognition_results(self, raw_results: str) -> Dict:
        """
        Парсит результаты распознавания (NDJSON формат)
        
        Args:
            raw_results: Сырой ответ API (несколько JSON объектов через \n)
            
        Returns:
            Структурированные результаты
        """
        results = {
            'text': '',
            'normalized_text': '',
            'words': [],
            'chunks': [],
            'speakers': [],
            'raw': []
        }
        
        for line in raw_results.strip().split('\n'):
            if not line:
                continue
            
            chunk = json.loads(line)
            results['raw'].append(chunk)
            
            if 'result' not in chunk:
                continue
            
            result = chunk['result']
            
            # Финальный результат
            if 'final' in result:
                final = result['final']
                if final.get('alternatives'):
                    alt = final['alternatives'][0]
                    results['text'] = alt.get('text', '')
                    results['words'].extend(alt.get('words', []))
                    
                    # Спикеры
                    if 'speaker_tag' in alt:
                        results['speakers'].append({
                            'speaker_tag': alt['speaker_tag'],
                            'text': alt['text']
                        })
            
            # Нормализованный текст
            if 'finalRefinement' in result:
                refinement = result['finalRefinement']
                if 'normalizedText' in refinement:
                    normalized = refinement['normalizedText']
                    results['normalized_text'] = normalized.get('text', '')
            
            # Сохраняем чанки для детального анализа
            results['chunks'].append(result)
        
        return results
    
    def save_transcript(
        self,
        results: Dict,
        output_path: Path,
        format: str = "txt"
    ):
        """
        Сохраняет транскрипт в файл
        
        Args:
            results: Результаты распознавания
            output_path: Путь для сохранения
            format: Формат (txt, json, srt)
        """
        output_path = Path(output_path)
        
        if format == "txt":
            # Простой текстовый формат
            text = results.get('normalized_text') or results.get('text')
            output_path.write_text(text, encoding='utf-8')
            
        elif format == "json":
            # Полный JSON
            output_path.write_text(
                json.dumps(results, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
        elif format == "srt":
            # SRT субтитры
            srt_content = self._convert_to_srt(results['words'])
            output_path.write_text(srt_content, encoding='utf-8')
        
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")
        
        print(f"💾 Транскрипт сохранён: {output_path}")
    
    def _convert_to_srt(self, words: List[Dict]) -> str:
        """Конвертирует слова с временными метками в SRT формат"""
        if not words:
            return ""
        
        srt_lines = []
        index = 1
        
        # Группируем слова в чанки по 5-7 слов
        chunk_size = 6
        
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            
            start_ms = int(chunk[0].get('startTimeMs', 0))
            end_ms = int(chunk[-1].get('endTimeMs', 0))
            
            text = ' '.join(w.get('text', '') for w in chunk)
            
            # Форматируем временные метки
            start_time = self._ms_to_srt_time(start_ms)
            end_time = self._ms_to_srt_time(end_ms)
            
            srt_lines.append(f"{index}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")
            
            index += 1
        
        return '\n'.join(srt_lines)
    
    def _ms_to_srt_time(self, ms: int) -> str:
        """Конвертирует миллисекунды в SRT формат времени"""
        seconds = ms // 1000
        milliseconds = ms % 1000
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def main():
    """Пример использования"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Yandex SpeechKit API v3 - точное распознавание русской речи"
    )
    parser.add_argument("uri", help="Ссылка на файл в Yandex Object Storage")
    parser.add_argument("--output", "-o", help="Путь для сохранения транскрипта")
    parser.add_argument("--format", choices=["txt", "json", "srt"], default="txt")
    parser.add_argument("--language", default="ru-RU")
    parser.add_argument("--model", default="general")
    parser.add_argument("--speakers", action="store_true", help="Метки спикеров")
    
    args = parser.parse_args()
    
    # Инициализация клиента
    stt = YandexSpeechKit()
    
    # Распознавание
    results = stt.transcribe_from_uri(
        uri=args.uri,
        language=args.language,
        model=args.model,
        speaker_labeling=args.speakers,
        literature_text=True
    )
    
    # Сохранение
    if args.output:
        stt.save_transcript(results, args.output, format=args.format)
    else:
        print("\n" + "="*80)
        print("ТРАНСКРИПТ:")
        print("="*80)
        print(results.get('normalized_text') or results.get('text'))
        print("="*80)


if __name__ == "__main__":
    main()

