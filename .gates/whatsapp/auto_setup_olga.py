#!/usr/bin/env python3
"""
Автоматическая настройка WhatsApp для Ольги
Пытается найти существующие credentials или создать структуру
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

def auto_setup():
    """Автоматическая настройка"""
    print("=" * 80)
    print("АВТОМАТИЧЕСКАЯ НАСТРОЙКА WHATSAPP ДЛЯ ОЛЬГИ")
    print("=" * 80)
    print()
    
    gates_dir = Path(__file__).parent.parent
    whatsapp_dir = Path(__file__).parent
    creds_dir = whatsapp_dir / 'credentials'
    creds_path = creds_dir / 'olga_credentials.json'
    
    # Проверяем существующие credentials
    possible_locations = [
        creds_path,
        gates_dir / 'whatsapp' / 'credentials.json',
        gates_dir / 'whatsapp_credentials.json',
    ]
    
    found_creds = None
    for loc in possible_locations:
        if loc.exists():
            try:
                with open(loc, 'r') as f:
                    creds = json.load(f)
                    if 'access_token' in creds and 'phone_number_id' in creds:
                        print(f"✅ Найдены credentials: {loc}")
                        found_creds = creds
                        break
            except:
                continue
    
    if found_creds:
        # Копируем в нужное место
        creds_dir.mkdir(parents=True, exist_ok=True)
        
        olga_creds = {
            'user': 'olga',
            'access_token': found_creds.get('access_token'),
            'phone_number_id': found_creds.get('phone_number_id'),
            'business_account_id': found_creds.get('business_account_id', ''),
            'webhook_verify_token': found_creds.get('webhook_verify_token', f'verify_token_olga_{datetime.now().timestamp()}'),
            'created_at': datetime.now().isoformat(),
            'source': str(found_creds.get('source', 'auto_detected'))
        }
        
        with open(creds_path, 'w') as f:
            json.dump(olga_creds, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Credentials скопированы в: {creds_path}")
        
        # Тестируем
        try:
            sys.path.insert(0, str(gates_dir))
            from whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate
            
            gate = WhatsAppMultiUserGate(user='olga')
            account = gate.test_token()
            
            if account['valid']:
                print(f"✅ Подключение успешно!")
                print(f"   Account: {account.get('name', 'N/A')}")
                return True
            else:
                print(f"⚠️  Токен невалиден: {account.get('error', 'Unknown')}")
                return False
        except Exception as e:
            print(f"⚠️  Ошибка теста: {e}")
            return False
    else:
        print("ℹ️  Существующие credentials не найдены")
        print()
        print("Для настройки WhatsApp Business API требуется:")
        print("1. Meta App с WhatsApp Product")
        print("2. Access Token и Phone Number ID")
        print()
        print("Эти данные можно получить только через Meta App Dashboard:")
        print("https://developers.facebook.com/apps/")
        print()
        print("После получения credentials создайте файл:")
        print(f"{creds_path}")
        print()
        print("С содержимым:")
        print(json.dumps({
            'user': 'olga',
            'access_token': 'YOUR_ACCESS_TOKEN',
            'phone_number_id': 'YOUR_PHONE_NUMBER_ID',
            'business_account_id': 'YOUR_BUSINESS_ACCOUNT_ID',
            'webhook_verify_token': 'verify_token_olga'
        }, indent=2))
        return False

if __name__ == '__main__':
    success = auto_setup()
    sys.exit(0 if success else 1)


