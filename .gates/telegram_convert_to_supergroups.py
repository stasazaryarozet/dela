#!/usr/bin/env python3
"""
Конвертирует обычные группы Ольги в супергруппы и включает полную историю
"""
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import MigrateChat
from telethon.tl.functions.channels import TogglePreHistoryHiddenRequest
import json
import time

with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']

client = TelegramClient('olga_session', olga['api_id'], olga['api_hash'])

async def convert_and_enable():
    await client.start(phone=olga['phone'])
    
    print("🔍 Ищу обычные группы для конвертации...\n")
    
    legacy_groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group and not hasattr(dialog.entity, 'megagroup'):
            try:
                perms = await client.get_permissions(dialog.entity, 'me')
                if perms.is_admin or perms.is_creator:
                    legacy_groups.append((dialog.name, dialog.entity, dialog.id))
            except:
                continue
    
    if not legacy_groups:
        print("✅ Все группы уже супергруппы\n")
        return
    
    print(f"📋 Найдено обычных групп: {len(legacy_groups)}\n")
    
    results = []
    for name, entity, chat_id in legacy_groups:
        try:
            print(f"�� {name}: конвертирую в супергруппу...")
            result = await client(MigrateChat(chat_id=chat_id))
            
            # Получаем новую супергруппу
            new_entity = await client.get_entity(result.chats[0])
            
            time.sleep(1)
            
            # Включаем полную историю
            await client(TogglePreHistoryHiddenRequest(
                channel=new_entity,
                enabled=False
            ))
            
            print(f"✅ {name}: конвертирована, история открыта")
            results.append({'name': name, 'old_id': chat_id, 'status': 'converted'})
            
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            results.append({'name': name, 'old_id': chat_id, 'status': f'error: {str(e)}'})
    
    with open('telegram_conversion_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Готово! Результаты: telegram_conversion_results.json")

with client:
    client.loop.run_until_complete(convert_and_enable())
