#!/usr/bin/env python3
"""
Настройка WhatsApp Cloud API через Meta App Dashboard
Согласно официальной документации: https://developers.facebook.com/docs/whatsapp/
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime

gates_dir = Path(__file__).parent.parent
meta_dir = gates_dir / 'meta'

def load_system_user_token():
    """Загрузить System User Token из .env или переменных окружения"""
    # Пробуем из .env файла
    env_path = meta_dir / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('META_SYSTEM_USER_TOKEN='):
                    return line.split('=', 1)[1].strip()
    
    # Пробуем из переменных окружения
    return os.environ.get('META_SYSTEM_USER_TOKEN')

def setup_whatsapp_cloud_api():
    """
    Настройка WhatsApp Cloud API для отправки и получения сообщений
    
    Согласно документации:
    - Cloud API: для отправки/получения сообщений
    - Business Management API: для управления аккаунтом и шаблонами
    - Phone Number: требуется для работы
    """
    print("=" * 80)
    print("НАСТРОЙКА WHATSAPP CLOUD API")
    print("=" * 80)
    print()
    print("📚 Документация: https://developers.facebook.com/docs/whatsapp/")
    print()
    
    # Загружаем Meta credentials
    credentials_path = meta_dir / 'credentials.json'
    if not credentials_path.exists():
        print("❌ Meta credentials не найдены")
        print("   Сначала запустите: python3 .gates/meta/deep_integration_auth.py")
        return None
    
    with open(credentials_path, 'r') as f:
        meta_creds = json.load(f)
    
    user_access_token = meta_creds.get('access_token')
    if not user_access_token:
        print("❌ Access token не найден")
        return None
    
    # Пробуем использовать System User Token (предпочтительно)
    system_user_token = load_system_user_token()
    access_token = system_user_token or user_access_token
    
    print("✅ Meta credentials загружены")
    print(f"   Пользователь: {meta_creds.get('user', {}).get('name', 'N/A')}")
    
    if system_user_token:
        print("   ✅ Используется System User Token (рекомендуется)")
    else:
        print("   ⚠️  Используется User Access Token (может не иметь прав на WhatsApp)")
        print("   💡 Для полного доступа создайте System User Token:")
        print("      python3 .gates/meta/save_system_user_token.py")
    print()
    
    # Шаг 1: Получаем бизнес-аккаунты через Business Management API
    print("📡 Шаг 1: Получение бизнес-аккаунтов...")
    
    try:
        businesses_response = requests.get(
            'https://graph.facebook.com/v18.0/me/businesses',
            params={'access_token': access_token}
        )
        
        if businesses_response.status_code == 200:
            businesses = businesses_response.json().get('data', [])
            print(f"   ✅ Найдено бизнес-аккаунтов: {len(businesses)}")
            
            if businesses:
                business = businesses[0]
                business_id = business.get('id')
                business_name = business.get('name', 'Unknown')
                
                print(f"   Используем: {business_name} (ID: {business_id})")
                print()
                
                # Шаг 2: Получаем WhatsApp Business Accounts
                print("📡 Шаг 2: Получение WhatsApp Business Accounts...")
                
                waba_response = requests.get(
                    f'https://graph.facebook.com/v18.0/{business_id}/owned_whatsapp_business_accounts',
                    params={'access_token': access_token}
                )
                
                if waba_response.status_code == 200:
                    waba_data = waba_response.json().get('data', [])
                    
                    if waba_data:
                        waba = waba_data[0]
                        waba_id = waba.get('id')
                        waba_name = waba.get('name', 'Unknown')
                        
                        print(f"   ✅ WhatsApp Business Account найден: {waba_name} (ID: {waba_id})")
                        print()
                        
                        # Шаг 3: Получаем номера телефонов
                        print("📡 Шаг 3: Получение номеров телефонов...")
                        
                        phone_response = requests.get(
                            f'https://graph.facebook.com/v18.0/{waba_id}/phone_numbers',
                            params={'access_token': access_token}
                        )
                        
                        phone_numbers = []
                        if phone_response.status_code == 200:
                            phone_data = phone_response.json().get('data', [])
                            phone_numbers = phone_data
                            print(f"   ✅ Найдено номеров: {len(phone_numbers)}")
                            
                            for i, phone in enumerate(phone_numbers, 1):
                                display_number = phone.get('display_phone_number', 'N/A')
                                phone_id = phone.get('id')
                                verified = phone.get('verified_name_status', 'UNKNOWN')
                                print(f"      {i}. {display_number} (ID: {phone_id}, Verified: {verified})")
                        else:
                            print(f"   ⚠️  Номера не найдены (Status: {phone_response.status_code})")
                            print(f"   Ответ: {phone_response.text[:200]}")
                        
                        # Шаг 4: Получаем Cloud API Access Token
                        # Для Cloud API нужен System User Token или Page Access Token
                        print()
                        print("📡 Шаг 4: Получение токена для Cloud API...")
                        
                        # Пробуем использовать Page Access Token из credentials
                        page_token = None
                        pages = meta_creds.get('pages', [])
                        
                        if pages:
                            # Используем первую страницу с токеном
                            for page in pages:
                                if page.get('access_token'):
                                    page_token = page.get('access_token')
                                    page_id = page.get('id')
                                    page_name = page.get('name', 'Unknown')
                                    print(f"   Используем Page Access Token от страницы: {page_name}")
                                    break
                        
                        if not page_token:
                            print("   ⚠️  Page Access Token не найден")
                            print("   Требуется создать System User в Business Settings")
                        
                        # Сохраняем WhatsApp credentials
                        whatsapp_creds_dir = gates_dir / 'whatsapp' / 'credentials'
                        whatsapp_creds_dir.mkdir(parents=True, exist_ok=True)
                        
                        whatsapp_credentials = {
                            'user': 'olga',
                            'whatsapp_business_account_id': waba_id,
                            'whatsapp_business_account_name': waba_name,
                            'business_id': business_id,
                            'business_name': business_name,
                            'phone_numbers': phone_numbers,
                            'primary_phone_number_id': phone_numbers[0].get('id') if phone_numbers else None,
                            'primary_phone_number': phone_numbers[0].get('display_phone_number') if phone_numbers else None,
                            'access_token': page_token or access_token,  # Используем Page Token или User Token
                            'user_access_token': access_token,
                            'page_access_token': page_token,
                            'api_version': 'v18.0',
                            'created_at': datetime.now().isoformat(),
                            'source': 'meta_deep_integration',
                            'note': 'Для Cloud API требуется System User Token или Page Access Token'
                        }
                        
                        olga_creds_path = whatsapp_creds_dir / 'olga_credentials.json'
                        with open(olga_creds_path, 'w') as f:
                            json.dump(whatsapp_credentials, f, indent=2, ensure_ascii=False)
                        
                        print()
                        print("=" * 80)
                        print("✅ WHATSAPP CLOUD API НАСТРОЕН")
                        print("=" * 80)
                        print()
                        print(f"📄 Credentials сохранены: {olga_creds_path}")
                        print()
                        print("📋 Информация:")
                        print(f"   WhatsApp Business Account: {waba_name}")
                        print(f"   Account ID: {waba_id}")
                        if phone_numbers:
                            print(f"   Номер телефона: {phone_numbers[0].get('display_phone_number')}")
                            print(f"   Phone Number ID: {phone_numbers[0].get('id')}")
                        print()
                        print("✅ Теперь можно использовать WhatsApp Cloud API:")
                        print("   python3 .gates/whatsapp/read_olga_messages.py")
                        print()
                        print("⚠️  Примечание:")
                        print("   Для полного доступа может потребоваться System User Token")
                        print("   Создайте System User в Business Settings → System Users")
                        print()
                        
                        return whatsapp_credentials
                    else:
                        print("   ⚠️  WhatsApp Business Accounts не найдены")
                        print()
                        print("   Требуется настройка через Meta App Dashboard:")
                        print("   1. Откройте: https://developers.facebook.com/apps/")
                        print("   2. Выберите ваше приложение")
                        print("   3. Добавьте продукт 'WhatsApp'")
                        print("   4. Настройте WhatsApp Business Account")
                        print("   5. Подключите номер телефона")
                        return None
                else:
                    print(f"   ❌ Ошибка получения WABA: {waba_response.status_code}")
                    print(f"   Ответ: {waba_response.text[:200]}")
                    return None
            else:
                print("   ⚠️  Бизнес-аккаунты не найдены")
                print()
                print("   Требуется создать Business Account в Meta Business Manager")
                return None
        else:
            print(f"   ❌ Ошибка получения бизнесов: {businesses_response.status_code}")
            print(f"   Ответ: {businesses_response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = setup_whatsapp_cloud_api()

