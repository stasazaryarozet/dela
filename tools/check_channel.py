import asyncio
from telethon import TelegramClient
from pathlib import Path
import sys

# Credentials
API_ID = 94575
API_HASH = 'a3406de8d171bb422bb6ddf3bbd800e2'

# Путь к сессии
SESSION_PATH = Path('olga/telegram-kanal-olga-rozet/anon.session')

async def main():
    print(f"📂 Используем сессию: {SESSION_PATH}")
    if not SESSION_PATH.exists():
        print("❌ Файл сессии не найден!")
        return

    client = TelegramClient(str(SESSION_PATH), API_ID, API_HASH)
    
    print("🔄 Подключение...")
    try:
        await client.connect()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

    print("🔐 Проверка авторизации...")
    if not await client.is_user_authorized():
        print("❌ Сессия не авторизована (требуется вход)")
        await client.disconnect()
        return
    
    me = await client.get_me()
    print(f"👤 Авторизован как: {me.first_name} {me.last_name or ''} (@{me.username})")

    channel = '@olgarozet'
    print(f"\n📱 Получение сообщений из {channel}...")
    
    try:
        messages = []
        async for message in client.iter_messages(channel, limit=20):
            messages.append(message)
        
        print(f"✅ Получено {len(messages)} сообщений.\n")
        print("=" * 60)
        
        for msg in reversed(messages):
            date = msg.date.strftime('%Y-%m-%d %H:%M') if msg.date else 'Unknown'
            sender = msg.sender.first_name if msg.sender else "Unknown"
            text = msg.text or '[медиа]'
            
            print(f"📅 {date} | 👤 {sender}")
            if msg.media:
                print(f"📎 {msg.media.__class__.__name__}")
            print(f"📝 {text[:200]}{'...' if len(text) > 200 else ''}")
            print("-" * 60)
            
    except Exception as e:
        print(f"❌ Ошибка при чтении: {e}")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
