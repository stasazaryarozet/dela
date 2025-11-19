#!/usr/bin/env python3
"""
Автоматическая миграция WhatsApp на Business Account
Минимальное человеческое участие - только подтверждение номера
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime

gates_dir = Path(__file__).parent.parent
meta_dir = gates_dir / 'meta'
whatsapp_dir = gates_dir / 'whatsapp'

def load_system_user_token():
    """Загрузить System User Token"""
    env_path = meta_dir / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('META_SYSTEM_USER_TOKEN='):
                    return line.split('=', 1)[1].strip()
    return os.environ.get('META_SYSTEM_USER_TOKEN')

def auto_setup_whatsapp_business():
    """
    Автоматическая настройка WhatsApp Business через Cloud API
    Требует только подтверждения номера телефона
    """
    print("=" * 80)
    print("АВТОМАТИЧЕСКАЯ МИГРАЦИЯ WHATSAPP НА BUSINESS ACCOUNT")
    print("=" * 80)
    print()
    print("🎯 Цель: Минимальное участие - только подтверждение номера")
    print()
    
    token = load_system_user_token()
    if not token:
        print("❌ System User Token не найден")
        print("   Сначала создайте токен: python3 .gates/meta/save_system_user_token.py")
        return None
    
    print("✅ System User Token загружен")
    print()
    
    # Шаг 1: Проверяем существующий WhatsApp Business Account
    print("📡 Шаг 1: Проверка существующего WhatsApp Business Account...")
    
    try:
        businesses_response = requests.get(
            'https://graph.facebook.com/v18.0/me/businesses',
            params={'access_token': token}
        )
        
        if businesses_response.status_code == 200:
            businesses = businesses_response.json().get('data', [])
            
            if businesses:
                business_id = businesses[0].get('id')
                business_name = businesses[0].get('name', 'Unknown')
                
                print(f"   ✅ Бизнес-аккаунт найден: {business_name} (ID: {business_id})")
                
                # Проверяем WhatsApp Business Accounts
                waba_response = requests.get(
                    f'https://graph.facebook.com/v18.0/{business_id}/owned_whatsapp_business_accounts',
                    params={'access_token': token}
                )
                
                if waba_response.status_code == 200:
                    waba_data = waba_response.json().get('data', [])
                    
                    if waba_data:
                        waba = waba_data[0]
                        waba_id = waba.get('id')
                        waba_name = waba.get('name', 'Unknown')
                        
                        print(f"   ✅ WhatsApp Business Account найден: {waba_name} (ID: {waba_id})")
                        
                        # Проверяем номера телефонов
                        phone_response = requests.get(
                            f'https://graph.facebook.com/v18.0/{waba_id}/phone_numbers',
                            params={'access_token': token}
                        )
                        
                        if phone_response.status_code == 200:
                            phones = phone_response.json().get('data', [])
                            
                            if phones:
                                phone = phones[0]
                                phone_id = phone.get('id')
                                display_number = phone.get('display_phone_number', 'N/A')
                                
                                print(f"   ✅ Номер телефона найден: {display_number} (ID: {phone_id})")
                                
                                # Сохраняем credentials
                                credentials_dir = whatsapp_dir / 'credentials'
                                credentials_dir.mkdir(parents=True, exist_ok=True)
                                
                                olga_credentials = {
                                    'user': 'olga',
                                    'whatsapp_business_account_id': waba_id,
                                    'whatsapp_business_account_name': waba_name,
                                    'business_id': business_id,
                                    'business_name': business_name,
                                    'phone_number_id': phone_id,
                                    'phone_number': display_number,
                                    'access_token': token,
                                    'api_version': 'v18.0',
                                    'created_at': datetime.now().isoformat(),
                                    'source': 'auto_migration',
                                    'status': 'ready'
                                }
                                
                                olga_creds_path = credentials_dir / 'olga_credentials.json'
                                with open(olga_creds_path, 'w') as f:
                                    json.dump(olga_credentials, f, indent=2, ensure_ascii=False)
                                
                                print()
                                print("=" * 80)
                                print("✅ МИГРАЦИЯ ЗАВЕРШЕНА")
                                print("=" * 80)
                                print()
                                print(f"📄 Credentials сохранены: {olga_creds_path}")
                                print()
                                print("✅ WhatsApp Business Account готов к использованию!")
                                print()
                                print("Теперь можно использовать:")
                                print("   python3 .gates/whatsapp/read_olga_messages.py")
                                print()
                                
                                return olga_credentials
                            else:
                                print("   ⚠️  Номера телефонов не найдены")
                                print()
                                print("   📋 Следующий шаг:")
                                print("      1. Откройте Meta App Dashboard")
                                print("      2. WhatsApp → API Setup → Add Phone Number")
                                print("      3. Выберите 'Use existing number'")
                                print("      4. Введите номер телефона Ольги")
                                print("      5. Подтвердите код из SMS")
                                print("      6. Запустите этот скрипт снова")
                                return None
                        else:
                            print(f"   ⚠️  Ошибка получения номеров: {phone_response.status_code}")
                            return None
                    else:
                        print("   ⚠️  WhatsApp Business Account не найден")
                        print()
                        print("   📋 Следующий шаг:")
                        print("      1. Откройте: https://developers.facebook.com/apps/848486860991509/")
                        print("      2. Добавьте продукт 'WhatsApp'")
                        print("      3. Создайте WhatsApp Business Account")
                        print("      4. Запустите этот скрипт снова")
                        return None
                else:
                    print(f"   ⚠️  Ошибка получения WABA: {waba_response.status_code}")
                    print(f"   Ответ: {waba_response.text[:200]}")
                    return None
            else:
                print("   ⚠️  Бизнес-аккаунты не найдены")
                return None
        else:
            print(f"   ❌ Ошибка получения бизнесов: {businesses_response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = auto_setup_whatsapp_business()
    
    if not result:
        print()
        print("=" * 80)
        print("📋 ИНСТРУКЦИЯ ПО РУЧНОЙ НАСТРОЙКЕ")
        print("=" * 80)
        print()
        print("Для завершения миграции выполните минимальные шаги:")
        print()
        print("1. Откройте: https://developers.facebook.com/apps/848486860991509/")
        print("2. Добавьте продукт 'WhatsApp' (если еще не добавлен)")
        print("3. WhatsApp → API Setup → Select Business Account")
        print("4. Add Phone Number → Use existing number")
        print("5. Введите номер телефона Ольги")
        print("6. Подтвердите код из SMS (единственное человеческое действие)")
        print("7. Запустите этот скрипт снова:")
        print("   python3 .gates/whatsapp/auto_migrate_to_business.py")
        print()
        print("После этого все будет автоматически настроено! ✅")


