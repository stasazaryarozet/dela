#!/usr/bin/env python3
"""
Проверяет статус всех групп Ольги: тип + видимость истории
"""
from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat
import json

with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']
client = TelegramClient('olga_session', olga['api_id'], olga['api_hash'])

async def verify_all():
    await client.start(phone=olga['phone'])
    
    print("🔍 Проверяю все группы Ольги...\n")
    
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            entity = dialog.entity
            
            try:
                perms = await client.get_permissions(entity, 'me')
                if not (perms.is_admin or perms.is_creator):
                    continue
                
                # Определяем тип
                if isinstance(entity, Channel):
                    if entity.megagroup:
                        group_type = "Супергруппа"
                        # Проверяем видимость истории
                        full = await client.get_entity(entity)
                        history_visible = "Видимая" if hasattr(full, 'hidden_prehistory') and not full.hidden_prehistory else "С момента добавления"
                    else:
                        group_type = "Канал"
                        history_visible = "N/A"
                elif isinstance(entity, Chat):
                    group_type = "Обычная группа (legacy)"
                    history_visible = "Всегда видимая (нет настройки)"
                else:
                    group_type = "Неизвестный"
                    history_visible = "N/A"
                
                groups.append({
                    'name': dialog.name,
                    'type': group_type,
                    'history': history_visible,
                    'id': dialog.id
                })
                
                print(f"{'✅' if group_type == 'Супергруппа' and 'Видимая' in history_visible else '⚠️'} {dialog.name}")
                print(f"   Тип: {group_type}")
                print(f"   История: {history_visible}\n")
                
            except Exception as e:
                print(f"❌ {dialog.name}: {str(e)}\n")
    
    # Сохраняем отчёт
    with open('telegram_groups_status.json', 'w', encoding='utf-8') as f:
        json.dump(groups, f, indent=2, ensure_ascii=False)
    
    # Статистика
    supergroups_ok = sum(1 for g in groups if g['type'] == 'Супергруппа' and 'Видимая' in g['history'])
    legacy = sum(1 for g in groups if 'legacy' in g['type'])
    
    print("=" * 60)
    print(f"📊 Статус:")
    print(f"   ✅ Супергруппы с открытой историей: {supergroups_ok}")
    print(f"   ⚠️ Обычные группы (требуют конвертации): {legacy}")
    print(f"   📄 Отчёт: telegram_groups_status.json")

with client:
    client.loop.run_until_complete(verify_all())
