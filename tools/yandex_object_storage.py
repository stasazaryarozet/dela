#!/usr/bin/env python3
"""
YANDEX OBJECT STORAGE - АВТОМАТИЧЕСКАЯ ЗАГРУЗКА

Автоматизация загрузки файлов в Yandex Object Storage через Yandex Cloud CLI.

Использование:
    from yandex_object_storage import YandexObjectStorage
    
    storage = YandexObjectStorage(bucket_name="my-speechkit-bucket")
    
    # Автоматическая загрузка файла
    public_url = storage.upload_file("video.mp4")
    
    # Использование с транскрипцией
    from yandex_speechkit import YandexSpeechKit
    stt = YandexSpeechKit()
    result = stt.transcribe_from_uri(public_url)

Требования:
- Yandex Cloud CLI (yc) установлен и настроен
- Сервисный аккаунт с ролями: storage.uploader, ai.speechkit-stt.user
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import hashlib


class YandexObjectStorage:
    """Менеджер для работы с Yandex Object Storage через CLI"""
    
    def __init__(
        self,
        bucket_name: str = "dela-speechkit-temp",
        folder_id: Optional[str] = None,
        auto_create_bucket: bool = True,
        public_access: bool = True
    ):
        """
        Инициализация
        
        Args:
            bucket_name: Имя bucket (должно быть уникальным)
            folder_id: ID каталога Yandex Cloud
            auto_create_bucket: Автоматически создать bucket если не существует
            public_access: Разрешить публичный доступ к файлам
        """
        self.bucket_name = bucket_name
        self.folder_id = folder_id or os.getenv('YANDEX_FOLDER_ID')
        self.public_access = public_access
        
        if not self.folder_id:
            raise ValueError(
                "Требуется folder_id. Установите переменную окружения: "
                "YANDEX_FOLDER_ID"
            )
        
        # Проверяем yc CLI
        if not self._check_yc_cli():
            raise RuntimeError(
                "Yandex Cloud CLI не установлен. "
                "Установите: brew install yandex-cloud/tap/yc"
            )
        
        # Настраиваем yc CLI
        self._configure_yc()
        
        # Создаём или проверяем bucket
        if auto_create_bucket:
            self._ensure_bucket_exists()
        
        print(f"✅ Yandex Object Storage готов")
        print(f"   Bucket: {self.bucket_name}")
    
    def _check_yc_cli(self) -> bool:
        """Проверяет наличие yc CLI"""
        try:
            result = subprocess.run(
                ['yc', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _configure_yc(self):
        """Настраивает yc CLI"""
        try:
            subprocess.run(
                ['yc', 'config', 'set', 'folder-id', self.folder_id],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Не удалось настроить yc CLI: {e}")
    
    def _ensure_bucket_exists(self):
        """Создаёт bucket если не существует"""
        # Проверяем существование
        if self._bucket_exists():
            print(f"✅ Bucket '{self.bucket_name}' существует")
            return
        
        # Создаём
        print(f"📦 Создаю bucket '{self.bucket_name}'...")
        
        try:
            cmd = [
                'yc', 'storage', 'bucket', 'create',
                '--name', self.bucket_name
            ]
            
            if self.public_access:
                cmd.extend(['--public-read'])
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            print(f"✅ Bucket создан")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            
            # Если bucket уже существует - это OK
            if 'already exists' in error_msg.lower():
                print(f"✅ Bucket '{self.bucket_name}' уже существует")
            else:
                raise RuntimeError(f"Не удалось создать bucket: {error_msg}")
    
    def _bucket_exists(self) -> bool:
        """Проверяет существование bucket"""
        try:
            result = subprocess.run(
                ['yc', 'storage', 'bucket', 'list', '--format', 'json'],
                check=True,
                capture_output=True,
                text=True
            )
            
            buckets = json.loads(result.stdout)
            return any(b.get('name') == self.bucket_name for b in buckets)
            
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return False
    
    def upload_file(
        self,
        file_path: Path | str,
        object_name: Optional[str] = None,
        ttl_days: Optional[int] = 7
    ) -> str:
        """
        Загружает файл в Object Storage и возвращает публичную ссылку
        
        Args:
            file_path: Путь к локальному файлу
            object_name: Имя объекта в bucket (по умолчанию: имя файла)
            ttl_days: Время жизни файла в днях (для временных файлов)
            
        Returns:
            Публичная ссылка на загруженный файл
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        # Определяем имя объекта
        if object_name is None:
            # Добавляем timestamp для уникальности
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()[:8]
            object_name = f"speechkit/{timestamp}_{file_hash}_{file_path.name}"
        
        print(f"📤 Загрузка в Object Storage...")
        print(f"   Файл: {file_path.name}")
        print(f"   Размер: {file_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        try:
            # Загружаем файл через S3 API
            result = subprocess.run(
                [
                    'yc', 'storage', 's3api', 'put-object',
                    '--bucket', self.bucket_name,
                    '--key', object_name,
                    '--body', str(file_path)
                ],
                check=True,
                capture_output=True,
                text=True
            )
            
            print(f"✅ Файл загружен: {object_name}")
            
            # Получаем публичную ссылку
            public_url = self._get_public_url(object_name)
            
            print(f"🔗 Публичная ссылка:")
            print(f"   {public_url}")
            
            return public_url
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise RuntimeError(f"Не удалось загрузить файл: {error_msg}")
    
    def _get_public_url(self, object_name: str) -> str:
        """
        Формирует публичную ссылку на объект
        
        Args:
            object_name: Имя объекта в bucket
            
        Returns:
            Публичная ссылка
        """
        # Формат: https://storage.yandexcloud.net/{bucket}/{object}
        return f"https://storage.yandexcloud.net/{self.bucket_name}/{object_name}"
    
    def delete_file(self, object_name: str):
        """
        Удаляет файл из Object Storage
        
        Args:
            object_name: Имя объекта в bucket
        """
        try:
            subprocess.run(
                [
                    'yc', 'storage', 's3api', 'delete-object',
                    '--bucket', self.bucket_name,
                    '--key', object_name
                ],
                check=True,
                capture_output=True
            )
            
            print(f"🗑️  Файл удалён: {object_name}")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Не удалось удалить файл: {e}")
    
    def list_files(self) -> list[Dict]:
        """
        Возвращает список файлов в bucket
        
        Returns:
            Список объектов
        """
        try:
            result = subprocess.run(
                [
                    'yc', 'storage', 's3api', 'list-objects',
                    '--bucket', self.bucket_name
                ],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Парсим вывод (в формате YAML/текст, не JSON)
            files = []
            for line in result.stdout.split('\n'):
                if 'key:' in line.lower():
                    key = line.split(':', 1)[-1].strip()
                    files.append({'name': key})
            
            return files
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Не удалось получить список файлов: {e}")
            return []
    
    def cleanup_old_files(self, days: int = 7):
        """
        Удаляет файлы старше указанного количества дней
        
        Args:
            days: Возраст файлов в днях
        """
        print(f"🧹 Очистка файлов старше {days} дней...")
        
        files = self.list_files()
        now = datetime.now()
        deleted = 0
        
        for obj in files:
            # Парсим дату из имени файла (если есть)
            if 'speechkit/' in obj.get('name', ''):
                try:
                    # Извлекаем timestamp из имени
                    parts = obj['name'].split('/')[-1].split('_')
                    if len(parts) >= 2:
                        date_str = f"{parts[0]}_{parts[1]}"
                        file_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                        
                        if (now - file_date).days > days:
                            self.delete_file(obj['name'])
                            deleted += 1
                except (ValueError, IndexError):
                    pass
        
        if deleted > 0:
            print(f"✅ Удалено файлов: {deleted}")
        else:
            print(f"✅ Нечего удалять")


def main():
    """Пример использования"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Yandex Object Storage - автоматическая загрузка файлов"
    )
    parser.add_argument("file", nargs='?', help="Файл для загрузки")
    parser.add_argument("--bucket", default="dela-speechkit-temp", help="Имя bucket")
    parser.add_argument("--list", action="store_true", help="Показать файлы в bucket")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Удалить файлы старше N дней")
    
    args = parser.parse_args()
    
    storage = YandexObjectStorage(bucket_name=args.bucket)
    
    if args.list:
        files = storage.list_files()
        print(f"\n📦 Файлы в bucket '{args.bucket}':")
        for f in files:
            print(f"   {f.get('name')}")
    
    elif args.cleanup is not None:
        storage.cleanup_old_files(days=args.cleanup)
    
    elif args.file:
        url = storage.upload_file(args.file)
        print(f"\n✅ Готово! Используй эту ссылку для транскрипции:")
        print(f"   {url}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

