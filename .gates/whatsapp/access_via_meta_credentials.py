#!/usr/bin/env python3
"""
Доступ к WhatsApp через Meta credentials
Использует долгоживущий токен из deep_integration_auth.py
"""
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

gates_dir = Path(__file__).parent.parent
meta_dir = gates_dir / 'meta'

def get_whatsapp_via_meta():
    """Получить доступ к WhatsApp через Meta credentials"""
    print("=" * 80)
    print("ДОСТУП К WHATSAPP ЧЕРЕЗ META CREDENTIALS")
    print("=" * 80)
    print()
    
    # Загружаем credentials из Meta
    credentials_path = meta_dir / 'credentials.json'
    if not credentials_path.exists():
        print("❌ Meta credentials не найдены")
        print("   Запустите: python3 .gates/meta/deep_integration_auth.py")
        return None
    
    with open(credentials_path, 'r') as f:
        meta_creds = json.load(f)
    
    access_token = meta_creds.get('access_token')
    if not access_token:
        print("❌ Access token не найден в credentials")
        return None
    
    print(f"✅ Meta credentials загружены")
    print(f"   Пользователь: {meta_creds.get('user', {}).get('name', 'N/A')}")
    print(f"   Страниц: {len(meta_creds.get('pages', []))}")
    print()
    
    # Пробуем получить WhatsApp Business Accounts
    print("📡 Получаю WhatsApp Business Accounts...")
    
    whatsapp_accounts = []
    whatsapp_phone_numbers = []
    
    # Метод 1: Через бизнес-аккаунты
    try:
        business_response = requests.get(
            'https://graph.facebook.com/v18.0/me/businesses',
            params={'access_token': access_token}
        )
        
        if business_response.status_code == 200:
            businesses = business_response.json().get('data', [])
            print(f"   Найдено бизнес-аккаунтов: {len(businesses)}")
            
            for business in businesses:
                try:
                    waba_response = requests.get(
                        f"https://graph.facebook.com/v18.0/{business['id']}/owned_whatsapp_business_accounts",
                        params={'access_token': access_token}
                    )
                    if waba_response.status_code == 200:
                        waba_data = waba_response.json().get('data', [])
                        whatsapp_accounts.extend(waba_data)
                        
                        # Получаем номера телефонов
                        for waba in waba_data:
                            try:
                                phone_response = requests.get(
                                    f"https://graph.facebook.com/v18.0/{waba['id']}/phone_numbers",
                                    params={'access_token': access_token}
                                )
                                if phone_response.status_code == 200:
                                    phones = phone_response.json().get('data', [])
                                    whatsapp_phone_numbers.extend(phones)
                            except:
                                pass
                except Exception as e:
                    print(f"   ⚠️  Ошибка для бизнеса {business.get('id')}: {e}")
        else:
            print(f"   ⚠️  Ошибка получения бизнесов: {business_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Ошибка: {e}")
    
    # Метод 2: Через страницы (если WhatsApp связан со страницей)
    print()
    print("📡 Проверяю страницы на наличие WhatsApp...")
    
    for page in meta_creds.get('pages', []):
        page_id = page.get('id')
        page_name = page.get('name', 'Unknown')
        page_token = page.get('access_token')
        
        try:
            # Проверяем, есть ли WhatsApp у страницы
            page_info = requests.get(
                f'https://graph.facebook.com/v18.0/{page_id}',
                params={
                    'fields': 'whatsapp_business_account',
                    'access_token': page_token
                }
            )
            
            if page_info.status_code == 200:
                page_data = page_info.json()
                if 'whatsapp_business_account' in page_data:
                    waba_id = page_data['whatsapp_business_account']['id']
                    print(f"   ✅ WhatsApp найден для страницы '{page_name}'")
                    
                    # Получаем информацию о WABA
                    waba_info = requests.get(
                        f'https://graph.facebook.com/v18.0/{waba_id}',
                        params={'access_token': page_token}
                    )
                    
                    if waba_info.status_code == 200:
                        waba_data = waba_info.json()
                        whatsapp_accounts.append({
                            'id': waba_id,
                            'name': waba_data.get('name', 'Unknown'),
                            'page_id': page_id,
                            'page_name': page_name,
                            'page_access_token': page_token
                        })
                        
                        # Получаем номера телефонов
                        try:
                            phone_response = requests.get(
                                f"https://graph.facebook.com/v18.0/{waba_id}/phone_numbers",
                                params={'access_token': page_token}
                            )
                            if phone_response.status_code == 200:
                                phones = phone_response.json().get('data', [])
                                whatsapp_phone_numbers.extend(phones)
                        except:
                            pass
        except Exception as e:
            pass
    
    print()
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 80)
    print()
    
    if whatsapp_accounts:
        print(f"✅ Найдено WhatsApp Business Accounts: {len(whatsapp_accounts)}")
        for i, waba in enumerate(whatsapp_accounts, 1):
            print(f"\n   {i}. {waba.get('name', 'Unknown')}")
            print(f"      ID: {waba.get('id')}")
            if 'page_name' in waba:
                print(f"      Страница: {waba.get('page_name')}")
        
        if whatsapp_phone_numbers:
            print(f"\n✅ Найдено номеров телефонов: {len(whatsapp_phone_numbers)}")
            for i, phone in enumerate(whatsapp_phone_numbers, 1):
                print(f"   {i}. {phone.get('display_phone_number', 'N/A')}")
                print(f"      Phone Number ID: {phone.get('id')}")
        
        # Сохраняем WhatsApp credentials для использования
        whatsapp_creds_dir = gates_dir / 'whatsapp' / 'credentials'
        whatsapp_creds_dir.mkdir(parents=True, exist_ok=True)
        
        # Используем первый WABA для Ольги
        if whatsapp_accounts:
            primary_waba = whatsapp_accounts[0]
            primary_phone = whatsapp_phone_numbers[0] if whatsapp_phone_numbers else None
            
            olga_credentials = {
                'user': 'olga',
                'access_token': primary_waba.get('page_access_token') or access_token,
                'phone_number_id': primary_phone.get('id') if primary_phone else None,
                'whatsapp_business_account_id': primary_waba.get('id'),
                'page_id': primary_waba.get('page_id'),
                'page_name': primary_waba.get('page_name'),
                'created_at': datetime.now().isoformat(),
                'source': 'meta_deep_integration'
            }
            
            olga_creds_path = whatsapp_creds_dir / 'olga_credentials.json'
            with open(olga_creds_path, 'w') as f:
                json.dump(olga_credentials, f, indent=2, ensure_ascii=False)
            
            print()
            print(f"✅ WhatsApp credentials сохранены: {olga_creds_path}")
            print()
            print("Теперь можно использовать для чтения сообщений:")
            print("   python3 .gates/whatsapp/read_olga_messages.py")
            
            return olga_credentials
    else:
        print("ℹ️  WhatsApp Business Accounts не найдены")
        print()
        print("Возможные причины:")
        print("  1. WhatsApp не настроен в Meta App Dashboard")
        print("  2. WhatsApp не связан со страницами")
        print("  3. Требуется дополнительная настройка через Meta App Dashboard")
        print()
        print("Для настройки WhatsApp:")
        print("  1. Откройте https://developers.facebook.com/apps/848486860991509/")
        print("  2. Добавьте продукт 'WhatsApp'")
        print("  3. Настройте WhatsApp Business Account")
        print("  4. Подключите номер телефона")
    
    return None

if __name__ == '__main__':
    result = get_whatsapp_via_meta()


