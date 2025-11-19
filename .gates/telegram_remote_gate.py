#!/usr/bin/env python3
"""
Telegram Remote Gate — публикация через удаленный Telegram-бот.

Существующий бот работает на Railway.app и архивирует контент на Яндекс.Диск.
Этот Gate позволяет публиковать сообщения через Bot API без доступа к архиву.

Для доступа к архиву: используйте telegram_archive_gate.py с YANDEX_DISK_TOKEN.
"""

import os
from datetime import datetime, timezone
from typing import Optional


class TelegramRemoteGate:
    """Упрощенный интерфейс для публикации через Telegram Bot API"""
    
    def __init__(self, bot_token: Optional[str] = None):
        """
        Инициализация Telegram Remote Gate.
        
        Args:
            bot_token: Token бота (по умолчанию из TELEGRAM_BOT_TOKEN)
        """
        self.bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
        
        if not self.bot_token:
            raise ValueError(
                "❌ TELEGRAM_BOT_TOKEN не указан.\n"
                "Установите: export TELEGRAM_BOT_TOKEN='your_token'"
            )
        
        try:
            from telegram import Bot
            self.bot = Bot(token=self.bot_token)
        except ImportError:
            raise ImportError(
                "❌ Требуется python-telegram-bot\n"
                "Установите: pip install python-telegram-bot"
            )
    
    # === AUTH ===
    
    async def test_token(self):
        """Проверка валидности Bot Token"""
        me = await self.bot.get_me()
        return {
            'valid': True,
            'bot_id': me.id,
            'username': me.username,
            'first_name': me.first_name
        }
    
    # === WRITE (Публикация) ===
    
    async def send_message(
        self, 
        chat_id: int, 
        text: str, 
        parse_mode: str = 'Markdown'
    ):
        """
        Отправить текстовое сообщение.
        
        Args:
            chat_id: ID чата или канала (например, -1001234567890)
            text: Текст сообщения
            parse_mode: 'Markdown' или 'HTML'
        
        Returns:
            {'message_id': ..., 'date': ...}
        """
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode
        )
        
        return {
            'message_id': message.message_id,
            'date': message.date.isoformat(),
            'chat_id': message.chat_id
        }
    
    async def send_photo(
        self, 
        chat_id: int, 
        photo_path: str, 
        caption: Optional[str] = None
    ):
        """
        Отправить фото.
        
        Args:
            chat_id: ID чата
            photo_path: Путь к файлу фото
            caption: Подпись к фото
        
        Returns:
            {'message_id': ..., 'date': ...}
        """
        with open(photo_path, 'rb') as photo:
            message = await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption
            )
        
        return {
            'message_id': message.message_id,
            'date': message.date.isoformat(),
            'chat_id': message.chat_id
        }
    
    async def send_video(
        self, 
        chat_id: int, 
        video_path: str, 
        caption: Optional[str] = None
    ):
        """
        Отправить видео.
        
        Args:
            chat_id: ID чата
            video_path: Путь к файлу видео
            caption: Подпись к видео
        
        Returns:
            {'message_id': ..., 'date': ...}
        """
        with open(video_path, 'rb') as video:
            message = await self.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=caption
            )
        
        return {
            'message_id': message.message_id,
            'date': message.date.isoformat(),
            'chat_id': message.chat_id
        }
    
    async def send_document(
        self, 
        chat_id: int, 
        document_path: str, 
        caption: Optional[str] = None
    ):
        """
        Отправить документ.
        
        Args:
            chat_id: ID чата
            document_path: Путь к файлу
            caption: Подпись к документу
        
        Returns:
            {'message_id': ..., 'date': ...}
        """
        with open(document_path, 'rb') as document:
            message = await self.bot.send_document(
                chat_id=chat_id,
                document=document,
                caption=caption
            )
        
        return {
            'message_id': message.message_id,
            'date': message.date.isoformat(),
            'chat_id': message.chat_id
        }
    
    # === READ (Минимальная информация) ===
    
    async def get_chat_info(self, chat_id: int):
        """
        Получить информацию о чате.
        
        Args:
            chat_id: ID чата
        
        Returns:
            {'id': ..., 'title': ..., 'type': ..., ...}
        """
        chat = await self.bot.get_chat(chat_id=chat_id)
        
        info = {
            'id': chat.id,
            'type': chat.type,
            'title': chat.title,
            'username': chat.username,
            'description': chat.description
        }
        
        # Количество участников (для групп)
        if chat.type in ['group', 'supergroup']:
            try:
                member_count = await self.bot.get_chat_member_count(chat_id=chat_id)
                info['member_count'] = member_count
            except:
                pass
        
        return info
    
    # === EXPORT ===
    
    async def export_substance(self):
        """
        Экспорт минимальной Substance (информация о боте).
        
        Note:
            Для полного экспорта архива используйте telegram_archive_gate.py
            с доступом к Яндекс.Диску.
        """
        bot_info = await self.test_token()
        
        return {
            'provider': 'telegram_remote',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'bot': bot_info,
                'note': 'Бот работает удаленно (Railway.app), архив на Яндекс.Диске'
            }
        }


# === CLI ===

async def main():
    """Тест Telegram Remote Gate"""
    try:
        gate = TelegramRemoteGate()
        
        print("🤖 Telegram Remote Gate\n")
        
        print("🔐 Проверка бота...")
        bot_info = await gate.test_token()
        print(f"✓ Бот: @{bot_info['username']} ({bot_info['first_name']})")
        print(f"  ID: {bot_info['bot_id']}\n")
        
        print("📊 Экспорт Substance...")
        substance = await gate.export_substance()
        print(f"✓ Provider: {substance['provider']}")
        print(f"  Note: {substance['data']['note']}\n")
        
        print("✅ Gate готов к публикации")
        print("\nИспользование:")
        print("  await gate.send_message(chat_id=-1001234567890, text='Hello')")
        print("  await gate.send_photo(chat_id=-1001234567890, photo_path='image.jpg')")
        
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
