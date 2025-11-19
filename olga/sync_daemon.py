#!/usr/bin/env python3
"""
Локальная автосинхронизация календарных сервисов
Запускается каждые 5 минут через launchd
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, '/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/.gates/calcom')
from calcom_gate import CalcomGateFull

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def sync():
    log("🔄 Запуск синхронизации...")
    
    gate = CalcomGateFull('cal_live_c7dba7d0cfbe9b741f496d56ef2f34e0')
    
    # 1. Проверяем изменения в Cal.com
    log("📊 Проверка Cal.com...")
    event_types = gate.get_event_types()
    bookings = gate.get_bookings()
    
    total_bookings = bookings.get('data', {}).get('totalCount', 0)
    log(f"   Event Types: {len(event_types)}")
    log(f"   Bookings: {total_bookings}")
    
    # 2. Обновляем content.md если нужно
    content_path = '/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/olga/olgaroset.ru/content.md'
    
    for et in event_types:
        if et.get('slug') == 'delo-40min':
            cal_description = et.get('description', '').strip()
            
            with open(content_path, 'r') as f:
                content = f.read()
            
            # Проверяем актуальность
            if cal_description and cal_description not in content:
                log("⚠️ Описание устарело, но обновление отложено (ручной контроль)")
            else:
                log("✅ Описание актуально")
    
    # 3. Синхронизируем Telegram
    log("📱 Синхронизация Telegram...")
    tg_script = '/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/olga/telegram-kanal-olga-rozet/telegram_content_sync.py'
    
    if os.path.exists(tg_script):
        result = os.system(f'cd "$(dirname "{tg_script}")" && python3 telegram_content_sync.py > /dev/null 2>&1')
        if result == 0:
            log("✅ Telegram обновлен")
        else:
            log("⚠️ Ошибка обновления Telegram")
    
    # 4. Коммитим изменения если есть
    repo_path = '/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/olga/olgaroset.ru'
    os.chdir(repo_path)
    
    # Проверяем есть ли изменения
    status = os.popen('git status --porcelain').read().strip()
    if status:
        log("📝 Найдены изменения, коммичу...")
        os.system('git add -A')
        os.system(f'git commit -m "🔄 Автосинхронизация {datetime.now().strftime("%Y-%m-%d %H:%M")}"')
        
        # Пытаемся запушить (если GitHub доступен)
        result = os.system('git push origin main 2>&1 | grep -q "Everything up-to-date\\|branch is up to date"')
        if result == 0:
            log("✅ Изменения отправлены в GitHub")
        else:
            log("⚠️ GitHub недоступен, изменения сохранены локально")
    else:
        log("✅ Изменений нет")
    
    log("✅ Синхронизация завершена\n")

if __name__ == '__main__':
    try:
        sync()
    except Exception as e:
        log(f"❌ Ошибка: {e}")
        sys.exit(1)


