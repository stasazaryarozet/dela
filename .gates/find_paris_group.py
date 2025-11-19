#!/usr/bin/env python3
"""Поиск группы с Париж в названии"""

import os
import sys
import asyncio
from pathlib import Path

gates_dir = Path(__file__).parent
sys.path.insert(0, str(gates_dir))

from telegram_group_gate import TelegramGroupGate

async def find_groups():
    gate = TelegramGroupGate()
    await gate.authenticate()
    
    print("🔍 Поиск групп с 'Париж' или '2025' в названии...\n")
    
    # Получаем все диалоги
    dialogs = await gate.client.get_dialogs()
    
    paris_groups = []
    all_groups = []
    
    for dialog in dialogs:
        if hasattr(dialog.entity, 'title'):
            title = dialog.entity.title
            all_groups.append(title)
            
            if 'париж' in title.lower() or 'paris' in title.lower() or '2025' in title.lower():
                paris_groups.append({
                    'title': title,
                    'id': dialog.entity.id,
                    'username': getattr(dialog.entity, 'username', None)
                })
    
    if paris_groups:
        print("✅ Найдены группы:")
        for group in paris_groups:
            print(f"\n  📱 {group['title']}")
            print(f"     ID: {group['id']}")
            if group['username']:
                print(f"     Username: @{group['username']}")
    else:
        print("❌ Группы с 'Париж' или '2025' не найдены")
        print("\n📋 Все группы/чаты:")
        for title in sorted(all_groups)[:20]:  # Показываем первые 20
            print(f"  • {title}")
        if len(all_groups) > 20:
            print(f"  ... и еще {len(all_groups) - 20} групп")
    
    await gate.close()

if __name__ == '__main__':
    asyncio.run(find_groups())

