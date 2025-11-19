#!/usr/bin/env python3
"""
Telegram Group Gate — чтение истории группы через Telethon (User API).

Использует Telethon для доступа к истории сообщений группы.
Требует авторизацию пользователя (один раз, сессия сохраняется).

Отличия от telegram_remote_gate.py:
- telegram_remote_gate.py: Bot API, только новые сообщения (webhooks)
- telegram_group_gate.py: User API (Telethon), полная история группы

Архитектура:
- Auth: Telethon сессия (один раз)
- Read: История сообщений группы
- Export: Substance формат
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Union
import json


class TelegramGroupGate:
    """Универсальный интерфейс для чтения истории Telegram группы через Telethon"""
    
    def __init__(
        self,
        api_id: Optional[str] = None,
        api_hash: Optional[str] = None,
        phone: Optional[str] = None,
        session_file: Optional[Union[str, Path]] = None
    ):
        """
        Инициализация Telegram Group Gate.
        
        Args:
            api_id: Telegram API ID (из my.telegram.org)
            api_hash: Telegram API Hash
            phone: Номер телефона (например, '+79161234567')
            session_file: Путь к файлу сессии (по умолчанию ~/.gates/telegram_session.session)
        
        Note:
            После первой авторизации сессия сохраняется, повторная авторизация не требуется.
        """
        self.api_id = api_id or os.environ.get('TELEGRAM_API_ID')
        self.api_hash = api_hash or os.environ.get('TELEGRAM_API_HASH')
        self.phone = phone or os.environ.get('TELEGRAM_PHONE')
        
        if not all([self.api_id, self.api_hash, self.phone]):
            raise ValueError(
                "❌ Требуются TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE\n"
                "Получите на https://my.telegram.org → API development tools"
            )
        
        # Файл сессии (по умолчанию в .gates/ или используем существующую из telegram-bot)
        if session_file is None:
            gates_dir = Path(__file__).parent
            # Проверяем существующую сессию из telegram-bot
            existing_session = gates_dir.parent / 'telegram-bot' / 'tools' / 'telegram_session.session'
            if existing_session.exists():
                session_file = existing_session
            else:
                session_file = gates_dir / 'telegram_session.session'
        else:
            session_file = Path(session_file)
        
        self.session_file = session_file
        self.client = None
        
        # Импорт Telethon
        try:
            from telethon import TelegramClient
            self.TelegramClient = TelegramClient
        except ImportError:
            raise ImportError(
                "❌ Требуется telethon\n"
                "Установите: pip install telethon"
            )
    
    # === AUTH ===
    
    async def authenticate(self):
        """Авторизация в Telegram (один раз, сессия сохраняется)"""
        if self.client:
            return
        
        self.client = self.TelegramClient(
            str(self.session_file),
            int(self.api_id),
            self.api_hash
        )
        
        # Пытаемся подключиться без переавторизации (если сессия существует)
        await self.client.connect()
        
        # Проверяем, авторизованы ли мы
        if not await self.client.is_user_authorized():
            # Требуется авторизация - запускаем интерактивную
            print(f"\n📱 Требуется авторизация в Telegram")
            print(f"   Telegram пришлет SMS с кодом на {self.phone}")
            print(f"   Введите код из SMS:\n")
            await self.client.start(phone=self.phone)
        else:
            print("✅ Используется существующая сессия")
        
        me = await self.client.get_me()
        return {
            'authenticated': True,
            'user_id': me.id,
            'username': me.username,
            'first_name': me.first_name,
            'phone': me.phone
        }
    
    async def test_connection(self):
        """Проверка подключения"""
        if not self.client:
            await self.authenticate()
        
        me = await self.client.get_me()
        return {
            'connected': True,
            'user': f"{me.first_name} (@{me.username or 'no_username'})",
            'user_id': me.id
        }
    
    # === READ ===
    
    async def get_chat_info(self, chat_identifier: Union[str, int]):
        """
        Получить информацию о чате/группе.
        
        Args:
            chat_identifier: Имя группы, username (@groupname) или ID чата
        
        Returns:
            {'id': ..., 'title': ..., 'type': ..., 'member_count': ...}
        """
        if not self.client:
            await self.authenticate()
        
        try:
            entity = await self.client.get_entity(chat_identifier)
            
            info = {
                'id': entity.id,
                'title': getattr(entity, 'title', None) or getattr(entity, 'first_name', 'Unknown'),
                'type': 'group' if hasattr(entity, 'title') else 'private',
                'username': getattr(entity, 'username', None)
            }
            
            # Количество участников (для групп)
            if hasattr(entity, 'participants_count'):
                info['member_count'] = entity.participants_count
            
            return info
        except Exception as e:
            raise ValueError(f"❌ Чат '{chat_identifier}' не найден: {e}")
    
    async def read_messages(
        self,
        chat_identifier: Union[str, int],
        limit: int = 100,
        offset_date: Optional[datetime] = None,
        min_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Прочитать сообщения из группы.
        
        Args:
            chat_identifier: Имя группы, username или ID
            limit: Максимальное количество сообщений
            offset_date: Читать сообщения до этой даты
            min_id: Минимальный ID сообщения (для инкрементального чтения)
        
        Returns:
            [{'message_id': ..., 'date': ..., 'text': ..., 'from_user': ..., 'media': ...}, ...]
        """
        if not self.client:
            await self.authenticate()
        
        try:
            entity = await self.client.get_entity(chat_identifier)
        except Exception as e:
            raise ValueError(f"❌ Чат '{chat_identifier}' не найден: {e}")
        
        messages = []
        
        # Формируем параметры для iter_messages (только не-None значения)
        iter_params = {'limit': limit}
        if offset_date is not None:
            iter_params['offset_date'] = offset_date
        if min_id is not None:
            iter_params['min_id'] = min_id
        
        async for message in self.client.iter_messages(entity, **iter_params):
            msg_data = {
                'message_id': message.id,
                'date': message.date.isoformat() if message.date else None,
                'text': message.text or message.message or '',
                'from_user': None,
                'media': None,
                'reply_to': None,
                'forward_from': None
            }
            
            # Отправитель
            if message.sender:
                msg_data['from_user'] = {
                    'id': message.sender.id,
                    'username': getattr(message.sender, 'username', None),
                    'first_name': getattr(message.sender, 'first_name', None),
                    'last_name': getattr(message.sender, 'last_name', None)
                }
            
            # Медиа
            if message.media:
                # Определяем тип медиа по классу
                media_class_name = message.media.__class__.__name__
                media_type = None
                
                if 'Photo' in media_class_name:
                    media_type = 'photo'
                elif 'Document' in media_class_name:
                    media_type = 'document'
                    # Проверяем атрибуты документа для уточнения типа
                    if hasattr(message.media, 'mime_type'):
                        mime = message.media.mime_type
                        if mime and 'video' in mime:
                            media_type = 'video'
                        elif mime and 'audio' in mime:
                            media_type = 'audio'
                elif 'Video' in media_class_name:
                    media_type = 'video'
                elif 'Audio' in media_class_name:
                    media_type = 'audio'
                elif 'Voice' in media_class_name:
                    media_type = 'voice'
                elif 'VideoNote' in media_class_name or 'Round' in media_class_name:
                    media_type = 'video_note'
                
                if media_type:
                    msg_data['media'] = {
                        'type': media_type,
                        'class_name': media_class_name
                    }
                    
                    # Дополнительная информация о файле
                    if hasattr(message, 'file') and message.file:
                        msg_data['media']['file_size'] = message.file.size
                        msg_data['media']['mime_type'] = getattr(message.file, 'mime_type', None)
                    elif hasattr(message.media, 'size'):
                        msg_data['media']['file_size'] = message.media.size
                    if hasattr(message.media, 'mime_type'):
                        msg_data['media']['mime_type'] = message.media.mime_type
            
            # Ответ на сообщение
            if message.reply_to:
                msg_data['reply_to'] = {
                    'message_id': message.reply_to.reply_to_msg_id
                }
            
            # Пересланное сообщение
            if message.fwd_from:
                msg_data['forward_from'] = {
                    'date': message.fwd_from.date.isoformat() if message.fwd_from.date else None,
                    'from_id': getattr(message.fwd_from, 'from_id', None)
                }
            
            messages.append(msg_data)
        
        return messages
    
    async def get_group_members(self, chat_identifier: Union[str, int]) -> List[Dict]:
        """
        Получить список участников группы.
        
        Args:
            chat_identifier: Имя группы или ID
        
        Returns:
            [{'id': ..., 'username': ..., 'first_name': ...}, ...]
        """
        if not self.client:
            await self.authenticate()
        
        try:
            entity = await self.client.get_entity(chat_identifier)
        except Exception as e:
            raise ValueError(f"❌ Чат '{chat_identifier}' не найден: {e}")
        
        members = []
        
        try:
            async for user in self.client.iter_participants(entity):
                members.append({
                    'id': user.id,
                    'username': getattr(user, 'username', None),
                    'first_name': getattr(user, 'first_name', None),
                    'last_name': getattr(user, 'last_name', None),
                    'is_bot': getattr(user, 'bot', False)
                })
        except Exception as e:
            # Некоторые группы не позволяют получать список участников
            return []
        
        return members
    
    # === EXPORT ===
    
    async def export_substance(
        self,
        chat_identifier: Union[str, int],
        messages_limit: int = 500,
        include_members: bool = True
    ) -> Dict:
        """
        Экспорт Substance из группы.
        
        Args:
            chat_identifier: Имя группы или ID
            messages_limit: Количество сообщений для экспорта
            include_members: Включить список участников
        
        Returns:
            {
                'provider': 'telegram_group',
                'timestamp': '...',
                'chat': {...},
                'messages': [...],
                'members': [...],
                'statistics': {...}
            }
        """
        if not self.client:
            await self.authenticate()
        
        # Информация о чате
        chat_info = await self.get_chat_info(chat_identifier)
        
        # Сообщения
        messages = await self.read_messages(chat_identifier, limit=messages_limit)
        
        # Участники
        members = []
        if include_members:
            try:
                members = await self.get_group_members(chat_identifier)
            except:
                pass
        
        # Статистика
        statistics = {
            'total_messages': len(messages),
            'total_members': len(members),
            'messages_with_media': sum(1 for m in messages if m.get('media')),
            'messages_with_text': sum(1 for m in messages if m.get('text')),
            'date_range': None
        }
        
        if messages:
            dates = [m['date'] for m in messages if m.get('date')]
            if dates:
                statistics['date_range'] = {
                    'oldest': min(dates),
                    'newest': max(dates)
                }
        
        substance = {
            'provider': 'telegram_group',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'chat': chat_info,
            'messages': messages,
            'members': members,
            'statistics': statistics
        }
        
        return substance
    
    async def close(self):
        """Закрыть соединение"""
        if self.client:
            await self.client.disconnect()
            self.client = None


# === CLI ===

async def main():
    """Тест Telegram Group Gate"""
    import sys
    
    try:
        gate = TelegramGroupGate()
        
        print("📱 Telegram Group Gate\n")
        
        # Проверка подключения
        print("🔐 Проверка подключения...")
        connection = await gate.test_connection()
        print(f"✓ Подключен как: {connection['user']}\n")
        
        # Если указан чат как аргумент
        if len(sys.argv) > 1:
            chat_name = sys.argv[1]
        else:
            print("Введите имя группы (или username с @):")
            chat_name = input("Группа: ").strip()
        
        if not chat_name:
            print("❌ Имя группы не указано")
            return
        
        # Информация о чате
        print(f"\n📊 Информация о группе '{chat_name}'...")
        chat_info = await gate.get_chat_info(chat_name)
        print(f"✓ Название: {chat_info['title']}")
        print(f"  ID: {chat_info['id']}")
        print(f"  Тип: {chat_info['type']}")
        if 'member_count' in chat_info:
            print(f"  Участников: {chat_info['member_count']}")
        
        # Чтение сообщений
        print(f"\n📬 Чтение сообщений (лимит: 50)...")
        messages = await gate.read_messages(chat_name, limit=50)
        print(f"✓ Прочитано сообщений: {len(messages)}")
        
        if messages:
            print(f"\nПоследние сообщения:")
            for msg in messages[:5]:
                user = msg.get('from_user', {})
                user_name = user.get('first_name', 'Unknown') if user else 'Unknown'
                text_preview = msg.get('text', '')[:50] or '[медиа]'
                print(f"  [{msg['date']}] {user_name}: {text_preview}")
        
        # Экспорт Substance
        print(f"\n📦 Экспорт Substance...")
        substance = await gate.export_substance(chat_name, messages_limit=100)
        print(f"✓ Экспортировано:")
        print(f"  Сообщений: {substance['statistics']['total_messages']}")
        print(f"  Участников: {substance['statistics']['total_members']}")
        print(f"  С медиа: {substance['statistics']['messages_with_media']}")
        
        # Сохранение Substance
        output_file = f"substance_telegram_{chat_info['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(substance, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Сохранено: {output_file}")
        
        await gate.close()
        
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

