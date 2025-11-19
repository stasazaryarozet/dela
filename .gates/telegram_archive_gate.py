#!/usr/bin/env python3
"""
Telegram Archive Gate — интеграция существующего Telegram-бота в Gates Architecture.

Существующий бот (telegram-bot/tools/telegram_bot_setup.py):
- Архивирует контент из чатов (видео, аудио, текст, фото, документы)
- Хранит в ~/TelegramArchive/ или Яндекс.Диске (зашифровано)
- Работает автономно (Railway.app или локально)

Этот Gate предоставляет:
- Чтение архивированного контента
- Экспорт Substance (метаданные + контент)
- Публикация в каналы (через существующий Bot API)
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional


class TelegramArchiveGate:
    """Универсальный интерфейс к архиву Telegram-бота"""
    
    def __init__(
        self, 
        archive_root: Optional[Path] = None,
        bot_token: Optional[str] = None,
        yandex_disk_token: Optional[str] = None
    ):
        """
        Инициализация Telegram Archive Gate.
        
        Args:
            archive_root: Путь к локальному архиву (если есть)
            bot_token: Token бота (для публикации, по умолчанию из TELEGRAM_BOT_TOKEN)
            yandex_disk_token: Token Яндекс.Диска (для доступа к удаленному архиву)
        
        Note:
            Бот работает удаленно (Railway.app), архив на Яндекс.Диске (зашифрован).
            Для доступа к архиву требуется yandex_disk_token.
        """
        # Локальный архив (опционально, может не существовать)
        if archive_root is None:
            archive_root = Path.home() / 'TelegramArchive'
        
        self.archive_root = Path(archive_root)
        self.has_local_archive = self.archive_root.exists() and any(self.archive_root.iterdir())
        
        # База обработанных файлов (глобальная дедупликация)
        self.processed_files_db = self.archive_root / 'processed_files.json'
        
        # Bot Token (для публикации через Bot API)
        self.bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
        
        if self.bot_token:
            from telegram import Bot
            self.bot = Bot(token=self.bot_token)
        else:
            self.bot = None
        
        # Яндекс.Диск (удаленный архив)
        self.yandex_disk_token = yandex_disk_token or os.environ.get('YANDEX_DISK_TOKEN')
        self.yandex_client = None
        
        if self.yandex_disk_token:
            try:
                import yadisk
                self.yandex_client = yadisk.YaDisk(token=self.yandex_disk_token)
                # Проверка токена
                if not self.yandex_client.check_token():
                    self.yandex_client = None
            except ImportError:
                pass  # yadisk не установлен
    
    # === AUTH ===
    
    async def test_token(self):
        """Проверка валидности Bot Token"""
        if not self.bot:
            return {'valid': False, 'error': 'Bot Token не указан'}
        
        me = await self.bot.get_me()
        return {
            'valid': True,
            'bot_id': me.id,
            'username': me.username,
            'first_name': me.first_name
        }
    
    # === READ (Архив) ===
    
    def get_chats(self) -> List[Dict]:
        """
        Получить список всех чатов в архиве.
        
        Returns:
            [{'chat_id': ..., 'chat_name': ..., 'path': ...}, ...]
        """
        chats = []
        
        # Локальный архив
        if self.has_local_archive:
            for chat_dir in self.archive_root.iterdir():
                if chat_dir.is_dir() and '_' in chat_dir.name:
                    # Формат: {chat_id}_{chat_name}
                    try:
                        chat_id_str, chat_name = chat_dir.name.split('_', 1)
                        chats.append({
                            'chat_id': int(chat_id_str),
                            'chat_name': chat_name,
                            'path': str(chat_dir),
                            'source': 'local'
                        })
                    except ValueError:
                        continue
        
        # Удаленный архив (Яндекс.Диск)
        if self.yandex_client:
            try:
                # Список папок в /TelegramArchive на Яндекс.Диске
                for item in self.yandex_client.listdir('/TelegramArchive'):
                    if item.type == 'dir' and '_' in item.name:
                        try:
                            chat_id_str, chat_name = item.name.split('_', 1)
                            # Проверить, не добавлен ли уже (дубль из локального)
                            if not any(c['chat_id'] == int(chat_id_str) for c in chats):
                                chats.append({
                                    'chat_id': int(chat_id_str),
                                    'chat_name': chat_name,
                                    'path': f'/TelegramArchive/{item.name}',
                                    'source': 'yandex_disk'
                                })
                        except (ValueError, AttributeError):
                            continue
            except:
                pass  # Яндекс.Диск недоступен
        
        return chats
    
    def get_chat_content(
        self, 
        chat_id: Optional[int] = None, 
        chat_name: Optional[str] = None,
        content_type: str = 'all'
    ) -> Dict:
        """
        Получить контент из чата.
        
        Args:
            chat_id: ID чата
            chat_name: Название чата (если chat_id неизвестен)
            content_type: 'videos', 'audio', 'text', 'photos', 'documents', 'all'
        
        Returns:
            {'videos': [...], 'audio': [...], 'text': [...], ...}
        """
        # Найти директорию чата
        chat_dir = None
        
        if chat_id:
            for d in self.archive_root.iterdir():
                if d.is_dir() and d.name.startswith(f"{chat_id}_"):
                    chat_dir = d
                    break
        elif chat_name:
            for d in self.archive_root.iterdir():
                if d.is_dir() and chat_name.lower() in d.name.lower():
                    chat_dir = d
                    break
        
        if not chat_dir:
            return {}
        
        content = {}
        
        # Типы контента
        types = ['videos', 'audio', 'voice', 'photos', 'documents', 'text'] if content_type == 'all' else [content_type]
        
        for ctype in types:
            type_dir = chat_dir / ctype
            if type_dir.exists():
                files = list(type_dir.glob('*'))
                content[ctype] = [str(f) for f in files]
        
        return content
    
    def get_metadata(
        self, 
        chat_id: Optional[int] = None,
        chat_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Получить метаданные сообщений из чата.
        
        Args:
            chat_id: ID чата
            chat_name: Название чата
            limit: Количество последних метаданных
        
        Returns:
            [{'message_id': ..., 'date': ..., 'file': ..., ...}, ...]
        """
        # Найти директорию чата
        chat_dir = None
        
        if chat_id:
            for d in self.archive_root.iterdir():
                if d.is_dir() and d.name.startswith(f"{chat_id}_"):
                    chat_dir = d
                    break
        elif chat_name:
            for d in self.archive_root.iterdir():
                if d.is_dir() and chat_name.lower() in d.name.lower():
                    chat_dir = d
                    break
        
        if not chat_dir:
            return []
        
        metadata_dir = chat_dir / 'metadata'
        if not metadata_dir.exists():
            return []
        
        # Получить JSON файлы метаданных
        metadata_files = sorted(
            metadata_dir.glob('*.json'),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:limit]
        
        metadata = []
        for mf in metadata_files:
            try:
                with open(mf, 'r') as f:
                    metadata.append(json.load(f))
            except:
                continue
        
        return metadata
    
    def get_processed_files_count(self) -> int:
        """Получить количество обработанных файлов (дедупликация)"""
        if not self.processed_files_db.exists():
            return 0
        
        with open(self.processed_files_db, 'r') as f:
            return len(json.load(f))
    
    # === WRITE (Публикация через Bot API) ===
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = 'Markdown'):
        """Отправить сообщение в чат"""
        if not self.bot:
            raise ValueError("❌ Bot Token не указан, публикация невозможна")
        
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode
        )
        
        return {
            'message_id': message.message_id,
            'date': message.date.isoformat()
        }
    
    async def send_photo(self, chat_id: int, photo_path: str, caption: Optional[str] = None):
        """Отправить фото в чат"""
        if not self.bot:
            raise ValueError("❌ Bot Token не указан, публикация невозможна")
        
        with open(photo_path, 'rb') as photo:
            message = await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption
            )
        
        return {
            'message_id': message.message_id,
            'date': message.date.isoformat()
        }
    
    # === EXPORT ===
    
    def export_substance(self, chats: Optional[List[str]] = None) -> Dict:
        """
        Экспорт Substance из архива Telegram-бота.
        
        Args:
            chats: Список названий чатов (если None — все чаты)
        
        Returns:
            {
                'provider': 'telegram_archive',
                'timestamp': '...',
                'data': {
                    'chats': [...],
                    'total_files': ...,
                    'recent_metadata': [...]
                }
            }
        """
        substance = {
            'provider': 'telegram_archive',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {}
        }
        
        # Получить все чаты
        all_chats = self.get_chats()
        
        if chats:
            # Фильтровать по названиям
            all_chats = [c for c in all_chats if any(name.lower() in c['chat_name'].lower() for name in chats)]
        
        substance['data']['chats'] = []
        
        for chat in all_chats:
            chat_data = {
                'chat_id': chat['chat_id'],
                'chat_name': chat['chat_name'],
                'content': self.get_chat_content(chat_id=chat['chat_id']),
                'recent_metadata': self.get_metadata(chat_id=chat['chat_id'], limit=50)
            }
            
            # Подсчитать количество файлов
            chat_data['file_counts'] = {
                ctype: len(files) for ctype, files in chat_data['content'].items()
            }
            
            substance['data']['chats'].append(chat_data)
        
        # Общая статистика
        substance['data']['total_chats'] = len(all_chats)
        substance['data']['total_processed_files'] = self.get_processed_files_count()
        
        return substance


# === CLI ===

async def main():
    """Тест Telegram Archive Gate"""
    try:
        gate = TelegramArchiveGate()
        
        print("📂 Telegram Archive Gate")
        print(f"   Архив: {gate.archive_root}\n")
        
        # Проверка Bot Token
        if gate.bot:
            print("🔐 Проверка Bot Token...")
            bot_info = await gate.test_token()
            if bot_info['valid']:
                print(f"✓ Бот: @{bot_info['username']} ({bot_info['first_name']})\n")
        else:
            print("⚠️  Bot Token не указан (публикация недоступна)\n")
        
        # Получить чаты
        print("📊 Чаты в архиве:")
        chats = gate.get_chats()
        
        for chat in chats:
            print(f"\n  📁 {chat['chat_name']}")
            print(f"     Chat ID: {chat['chat_id']}")
            
            # Контент
            content = gate.get_chat_content(chat_id=chat['chat_id'])
            for ctype, files in content.items():
                if files:
                    print(f"     {ctype}: {len(files)} файлов")
            
            # Последние метаданные
            metadata = gate.get_metadata(chat_id=chat['chat_id'], limit=5)
            if metadata:
                print(f"     Последнее сообщение: {metadata[0].get('date', 'N/A')}")
        
        print(f"\n📊 Всего обработано файлов: {gate.get_processed_files_count()}")
        
        print("\n📦 Экспорт Substance...")
        substance = gate.export_substance()
        print(f"✓ Экспортировано:")
        print(f"  Чатов: {substance['data']['total_chats']}")
        print(f"  Файлов: {substance['data']['total_processed_files']}")
        
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
