#!/usr/bin/env python3
"""
Настройка WhatsApp для Olga

Интерактивный скрипт для настройки WhatsApp Business API
"""
import os
import json
import sys
import secrets
from datetime import datetime
from pathlib import Path

# Добавляем путь к gates
gates_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(gates_dir))

def setup_olga_whatsapp():
    """Интерактивная настройка WhatsApp для Olga"""
    print("=" * 80)
    print("НАСТРОЙКА WHATSAPP ДЛЯ OLGA")
    print("=" * 80)
    print()
    
    print("Для настройки WhatsApp Business API:")
    print("1. Откройте https://developers.facebook.com/apps/")
    print("2. Создайте новое приложение или выберите существующее")
    print("3. Добавьте продукт 'WhatsApp'")
    print("4. Настройте WhatsApp Business Account")
    print("5. Получите credentials из раздела 'Getting Started'")
    print()
    
    print("Введите credentials:")
    print()
    
    access_token = input("Access Token (EAA...): ").strip()
    if not access_token:
        print("❌ Access Token обязателен")
        return False
    
    phone_number_id = input("Phone Number ID: ").strip()
    if not phone_number_id:
        print("❌ Phone Number ID обязателен")
        return False
    
    business_account_id = input("Business Account ID (опционально): ").strip()
    
    webhook_verify_token = input("Webhook Verify Token (опционально, будет сгенерирован): ").strip()
    if not webhook_verify_token:
        webhook_verify_token = secrets.token_urlsafe(32)
        print(f"  ✓ Сгенерирован токен: {webhook_verify_token[:20]}...")
    
    credentials = {
        'user': 'olga',
        'access_token': access_token,
        'phone_number_id': phone_number_id,
        'business_account_id': business_account_id or '',
        'webhook_verify_token': webhook_verify_token,
        'created_at': datetime.now().isoformat()
    }
    
    # Сохраняем credentials
    credentials_dir = Path(__file__).parent.parent / 'credentials'
    credentials_dir.mkdir(parents=True, exist_ok=True)
    
    credentials_path = credentials_dir / 'olga_credentials.json'
    
    with open(credentials_path, 'w') as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"✅ Credentials сохранены: {credentials_path}")
    print()
    
    # Тестируем подключение
    print("🔐 Тестирую подключение...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from whatsapp_multi_user_gate import WhatsAppMultiUserGate
        gate = WhatsAppMultiUserGate(user='olga')
        account = gate.test_token()
        
        if account['valid']:
            print(f"✅ Подключение успешно!")
            print(f"   Account: {account.get('name', 'N/A')}")
            print(f"   ID: {account.get('business_account_id', 'N/A')}")
        else:
            print(f"❌ Ошибка подключения: {account.get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 80)
    print("✅ НАСТРОЙКА ЗАВЕРШЕНА")
    print("=" * 80)
    print()
    print("Следующие шаги:")
    print("1. Настройте webhook в Meta App Dashboard")
    print("2. Используйте WhatsAppMultiUserGate(user='olga') для работы")
    print()
    
    return True

if __name__ == '__main__':
    success = setup_olga_whatsapp()
    sys.exit(0 if success else 1)

