#!/usr/bin/env python3
"""
Для максимальной интеграции: либо получить админа, либо выйти из группы
"""
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
import json

with open('telegram_credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)

olga = creds['olga']
client = TelegramClient('olga_session', olga['api_id'], olga['api_hash'])

async def handle_no_admin_groups():
    await client.start(phone=olga['phone'])
    
    print("🔍 Ищу группы, где Ольга НЕ администратор...\n")
    
    no_admin_groups = []
    
    async for dialog in client.iter_dialogs():
        if dialog.is_group or (dialog.is_channel and hasattr(dialog.entity, 'megagroup')):
            try:
                perms = await client.get_permissions(dialog.entity, 'me')
                
                if not (perms.is_admin or perms.is_creator):
                    no_admin_groups.append({
                        'name': dialog.name,
                        'id': dialog.id,
                        'participants': getattr(dialog.entity, 'participants_count', 'N/A')
                    })
            except:
                continue
    
    if not no_admin_groups:
        print("✅ Ольга администратор во всех группах\n")
        return
    
    print(f"⚠️ Найдено групп без админ-прав: {len(no_admin_groups)}\n")
    
    for group in no_admin_groups:
        print(f"📍 {group['name']}")
        print(f"   ID: {group['id']}")
        print(f"   Участников: {group['participants']}")
        print(f"   → Невозможна полная интеграция (нет доступа к истории для новых)\n")
    
    with open('telegram_no_admin_groups.json', 'w', encoding='utf-8') as f:
        json.dump(no_admin_groups, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print("📋 Для максимальной интеграции ○:")
    print("   1. Попросить админа дать права Ольге")
    print("   2. Или покинуть группу (если она не критична)")
    print("\n📄 Список: telegram_no_admin_groups.json")

with client:
    client.loop.run_until_complete(handle_no_admin_groups())
