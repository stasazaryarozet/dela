#!/usr/bin/env python3
"""
Экспорт всей истории группы "ПАРИЖ сентябрь 25" через аккаунт Ольги
"""
from telethon import TelegramClient
import json
import asyncio
from datetime import datetime

with open('telegram_credentials.json', 'r') as f:
    creds = json.load(f)['olga']

client = TelegramClient('olga_session', creds['api_id'], creds['api_hash'])

async def export_paris_group():
    await client.start()
    
    group_id = 4906876993  # ПАРИЖ сентябрь 25
    
    print(f"📥 Экспортирую историю группы ПАРИЖ сентябрь 25...")
    print(f"   ID: {group_id}\n")
    
    messages = []
    
    async for message in client.iter_messages(group_id, limit=None):
        msg_data = {
            'id': message.id,
            'date': message.date.isoformat() if message.date else None,
            'sender_id': message.sender_id,
            'text': message.text,
            'media': str(message.media) if message.media else None,
            'reply_to': message.reply_to_msg_id,
            'forwards': message.forwards
        }
        
        # Получаем имя отправителя
        if message.sender_id:
            try:
                sender = await client.get_entity(message.sender_id)
                msg_data['sender_name'] = getattr(sender, 'first_name', '') + ' ' + (getattr(sender, 'last_name', '') or '')
                msg_data['sender_username'] = getattr(sender, 'username', None)
            except:
                msg_data['sender_name'] = 'Unknown'
        
        messages.append(msg_data)
        
        if len(messages) % 50 == 0:
            print(f"   Загружено сообщений: {len(messages)}")
    
    # Сортируем по дате (от старых к новым)
    messages.sort(key=lambda x: x['date'] if x['date'] else '')
    
    # Сохраняем
    output = {
        'group_name': 'ПАРИЖ сентябрь 25',
        'group_id': group_id,
        'exported_at': datetime.now().isoformat(),
        'total_messages': len(messages),
        'first_message_date': messages[0]['date'] if messages else None,
        'last_message_date': messages[-1]['date'] if messages else None,
        'messages': messages
    }
    
    filename = f"paris_sept_25_full_history.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Экспорт завершён!")
    print(f"   Всего сообщений: {len(messages)}")
    if messages:
        print(f"   Период: {messages[0]['date'][:10]} — {messages[-1]['date'][:10]}")
    print(f"   Файл: {filename}")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(export_paris_group())
