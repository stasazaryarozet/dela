#!/usr/bin/env python3
"""
Включает доступ к полной истории для новых участников в группах Ольги
"""
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import TogglePreHistoryHiddenRequest
import json

# Загружаем credentials
with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']

client = TelegramClient(
    'olga_session',
    olga['api_id'],
    olga['api_hash']
)

async def enable_full_history():
    await client.start(phone=olga['phone'])
    
    print("🔍 Ищу группы, где Ольга — администратор...\n")
    
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            entity = dialog.entity
            
            # Проверяем, есть ли права администратора
            try:
                perms = await client.get_permissions(entity, 'me')
                if perms.is_admin or perms.is_creator:
                    groups.append((dialog.name, entity, dialog.id))
            except:
                continue
    
    if not groups:
        print("❌ Не найдено групп с правами администратора")
        return
    
    print(f"✅ Найдено групп с админ-правами: {len(groups)}\n")
    
    results = []
    for name, entity, dialog_id in groups:
        try:
            # Включаем полную историю для новых участников
            await client(TogglePreHistoryHiddenRequest(
                channel=entity,
                enabled=False  # False = показывать историю
            ))
            print(f"✅ {name}: история открыта")
            results.append({'name': name, 'id': dialog_id, 'status': 'enabled'})
        except Exception as e:
            print(f"⚠️ {name}: {str(e)}")
            results.append({'name': name, 'id': dialog_id, 'status': f'error: {str(e)}'})
    
    # Сохраняем результаты
    with open('telegram_history_settings.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Готово! Настройки сохранены: telegram_history_settings.json")
    print(f"📊 Обработано групп: {len(results)}")

with client:
    client.loop.run_until_complete(enable_full_history())
