#!/usr/bin/env python3
"""
Яндекс.Диск интеграция для telegram-bot
Использует WebDAV API для загрузки файлов
"""

import os
import requests
from pathlib import Path
from typing import Optional

class YandexDiskUploader:
    """Загрузчик файлов на Яндекс.Диск через WebDAV"""
    
    def __init__(self, token: str):
        """
        Args:
            token: OAuth токен Яндекс.Диска
        """
        self.token = token
        self.base_url = "https://webdav.yandex.ru"
        
    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """
        Загружает файл на Яндекс.Диск
        
        Args:
            local_path: Путь к локальному файлу
            remote_path: Путь на Яндекс.Диске (например: /TelegramArchive/video.mp4)
            
        Returns:
            True если успешно, False если ошибка
        """
        if not local_path.exists():
            print(f"❌ Файл не найден: {local_path}")
            return False
            
        # Создаем родительские директории
        parent_dir = str(Path(remote_path).parent)
        self._create_directory(parent_dir)
        
        # Загружаем файл
        url = f"{self.base_url}{remote_path}"
        
        try:
            with open(local_path, 'rb') as f:
                response = requests.put(
                    url,
                    data=f,
                    headers={'Authorization': f'OAuth {self.token}'},
                    timeout=300  # 5 минут для больших файлов
                )
            
            if response.status_code in (201, 204):
                print(f"✅ Загружено: {remote_path}")
                return True
            else:
                print(f"❌ Ошибка загрузки: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при загрузке: {e}")
            return False
    
    def _create_directory(self, path: str) -> bool:
        """Создает директорию на Яндекс.Диске (рекурсивно)"""
        if path == '/' or not path:
            return True
            
        url = f"{self.base_url}{path}"
        
        try:
            response = requests.request(
                'MKCOL',
                url,
                headers={'Authorization': f'OAuth {self.token}'}
            )
            
            # 201 = создана, 405 = уже существует
            if response.status_code in (201, 405):
                return True
            elif response.status_code == 409:
                # Родительская директория не существует - создаем рекурсивно
                parent = str(Path(path).parent)
                if self._create_directory(parent):
                    return self._create_directory(path)
                return False
            else:
                print(f"⚠️  Ошибка создания директории {path}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Исключение при создании директории: {e}")
            return False


def upload_to_yandex(local_path: Path, remote_path: str, token: Optional[str] = None) -> bool:
    """
    Вспомогательная функция для загрузки файла
    
    Args:
        local_path: Путь к локальному файлу
        remote_path: Путь на Яндекс.Диске
        token: OAuth токен (если None, берется из YANDEX_DISK_TOKEN)
        
    Returns:
        True если успешно
    """
    token = token or os.environ.get('YANDEX_DISK_TOKEN')
    
    if not token:
        print("⚠️  YANDEX_DISK_TOKEN не установлен")
        return False
    
    uploader = YandexDiskUploader(token)
    return uploader.upload_file(local_path, remote_path)


if __name__ == '__main__':
    # Тест
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python3 yandex_storage.py <local_file> <remote_path>")
        print("Example: python3 yandex_storage.py test.txt /TelegramArchive/test.txt")
        sys.exit(1)
    
    local = Path(sys.argv[1])
    remote = sys.argv[2]
    
    success = upload_to_yandex(local, remote)
    sys.exit(0 if success else 1)

