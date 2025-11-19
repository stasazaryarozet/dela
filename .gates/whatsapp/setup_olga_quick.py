#!/usr/bin/env python3
"""
Быстрая настройка WhatsApp для Ольги
Интерактивный скрипт с минимальными вопросами
"""
import json
import secrets
from datetime import datetime
from pathlib import Path

def quick_setup():
    """Быстрая настройка"""
    print("=" * 80)
    print("БЫСТРАЯ НАСТРОЙКА WHATSAPP ДЛЯ ОЛЬГИ")
    print("=" * 80)
    print()
    print("Для получения credentials:")
    print("1. Откройте https://developers.facebook.com/apps/")
    print("2. Выберите приложение или создайте новое")
    print("3. Добавьте продукт 'WhatsApp'")
    print("4. В разделе 'Getting Started' найдите:")
    print("   - Access Token")
    print("   - Phone Number ID")
    print("   - Business Account ID (опционально)")
    print()
    
    access_token = input("Access Token (EAA...): ").strip()
    if not access_token:
        print("❌ Access Token обязателен")
        return False
    
    phone_number_id = input("Phone Number ID: ").strip()
    if not phone_number_id:
        print("❌ Phone Number ID обязателен")
        return False
    
    business_account_id = input("Business Account ID (Enter для пропуска): ").strip()
    
    webhook_token = secrets.token_urlsafe(32)
    
    creds = {
        'user': 'olga',
        'access_token': access_token,
        'phone_number_id': phone_number_id,
        'business_account_id': business_account_id or '',
        'webhook_verify_token': webhook_token,
        'created_at': datetime.now().isoformat()
    }
    
    creds_dir = Path(__file__).parent.parent / 'credentials'
    creds_dir.mkdir(parents=True, exist_ok=True)
    creds_path = creds_dir / 'olga_credentials.json'
    
    with open(creds_path, 'w') as f:
        json.dump(creds, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"✅ Credentials сохранены: {creds_path}")
    print()
    print("Тестирую подключение...")
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from whatsapp_multi_user_gate import WhatsAppMultiUserGate
        
        gate = WhatsAppMultiUserGate(user='olga')
        account = gate.test_token()
        
        if account['valid']:
            print(f"✅ Подключение успешно!")
            print(f"   Account: {account.get('name', 'N/A')}")
            return True
        else:
            print(f"⚠️  Ошибка подключения: {account.get('error', 'Unknown')}")
            print("   Проверьте правильность credentials")
            return False
    except Exception as e:
        print(f"⚠️  Ошибка теста: {e}")
        return False

if __name__ == '__main__':
    success = quick_setup()
    if success:
        print()
        print("✅ Готово! Теперь можно читать сообщения:")
        print("   python3 .gates/whatsapp/read_olga_messages.py")


