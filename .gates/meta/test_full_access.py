#!/usr/bin/env python3
"""
Тест полного доступа ко всем платформам Meta через System User Token
"""
import json
import os
import requests
from pathlib import Path

gates_dir = Path(__file__).parent.parent
meta_dir = gates_dir / 'meta'

def load_system_user_token():
    """Загрузить System User Token"""
    env_path = meta_dir / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('META_SYSTEM_USER_TOKEN='):
                    return line.split('=', 1)[1].strip()
    return os.environ.get('META_SYSTEM_USER_TOKEN')

def test_full_access():
    """Тест доступа ко всем платформам Meta"""
    print("=" * 80)
    print("ТЕСТ ПОЛНОГО ДОСТУПА К META ПЛАТФОРМАМ")
    print("=" * 80)
    print()
    
    token = load_system_user_token()
    if not token:
        print("❌ System User Token не найден")
        print("   Создайте токен: python3 .gates/meta/save_system_user_token.py")
        return False
    
    print("✅ System User Token загружен")
    print()
    
    results = {
        'businesses': False,
        'pages': False,
        'instagram': False,
        'whatsapp': False,
        'errors': []
    }
    
    # Тест 1: Business Management API
    print("📡 Тест 1: Business Management API...")
    try:
        response = requests.get(
            'https://graph.facebook.com/v18.0/me/businesses',
            params={'access_token': token}
        )
        if response.status_code == 200:
            businesses = response.json().get('data', [])
            print(f"   ✅ Найдено бизнес-аккаунтов: {len(businesses)}")
            results['businesses'] = True
            if businesses:
                print(f"      Первый: {businesses[0].get('name', 'Unknown')}")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            results['errors'].append(f"Businesses: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        results['errors'].append(f"Businesses: {e}")
    
    print()
    
    # Тест 2: Facebook Pages
    print("📡 Тест 2: Facebook Pages...")
    try:
        response = requests.get(
            'https://graph.facebook.com/v18.0/me/accounts',
            params={'access_token': token}
        )
        if response.status_code == 200:
            pages = response.json().get('data', [])
            print(f"   ✅ Найдено страниц: {len(pages)}")
            results['pages'] = True
            for i, page in enumerate(pages[:3], 1):
                print(f"      {i}. {page.get('name', 'Unknown')} (ID: {page.get('id')})")
                if page.get('access_token'):
                    print(f"         ✅ Page Access Token доступен")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            results['errors'].append(f"Pages: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        results['errors'].append(f"Pages: {e}")
    
    print()
    
    # Тест 3: Instagram Accounts
    print("📡 Тест 3: Instagram Accounts...")
    try:
        # Получаем через Pages
        pages_response = requests.get(
            'https://graph.facebook.com/v18.0/me/accounts',
            params={'access_token': token, 'fields': 'id,name,instagram_business_account'}
        )
        if pages_response.status_code == 200:
            pages = pages_response.json().get('data', [])
            instagram_count = 0
            for page in pages:
                if page.get('instagram_business_account'):
                    instagram_count += 1
            if instagram_count > 0:
                print(f"   ✅ Найдено Instagram аккаунтов: {instagram_count}")
                results['instagram'] = True
            else:
                print(f"   ℹ️  Instagram аккаунты не найдены (возможно, не связаны со страницами)")
        else:
            print(f"   ❌ Ошибка: {pages_response.status_code}")
            results['errors'].append(f"Instagram: {pages_response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        results['errors'].append(f"Instagram: {e}")
    
    print()
    
    # Тест 4: WhatsApp Business Accounts
    print("📡 Тест 4: WhatsApp Business Accounts...")
    try:
        businesses_response = requests.get(
            'https://graph.facebook.com/v18.0/me/businesses',
            params={'access_token': token}
        )
        if businesses_response.status_code == 200:
            businesses = businesses_response.json().get('data', [])
            whatsapp_count = 0
            for business in businesses[:3]:
                waba_response = requests.get(
                    f"https://graph.facebook.com/v18.0/{business['id']}/owned_whatsapp_business_accounts",
                    params={'access_token': token}
                )
                if waba_response.status_code == 200:
                    waba_data = waba_response.json().get('data', [])
                    whatsapp_count += len(waba_data)
            
            if whatsapp_count > 0:
                print(f"   ✅ Найдено WhatsApp Business Accounts: {whatsapp_count}")
                results['whatsapp'] = True
            else:
                print(f"   ⚠️  WhatsApp Business Accounts не найдены")
                print(f"      Требуется настройка через Meta App Dashboard")
        else:
            print(f"   ❌ Ошибка: {businesses_response.status_code}")
            results['errors'].append(f"WhatsApp: {businesses_response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        results['errors'].append(f"WhatsApp: {e}")
    
    print()
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ТЕСТА")
    print("=" * 80)
    print()
    
    print(f"✅ Business Management: {'Доступен' if results['businesses'] else 'Недоступен'}")
    print(f"✅ Facebook Pages: {'Доступны' if results['pages'] else 'Недоступны'}")
    print(f"✅ Instagram: {'Доступен' if results['instagram'] else 'Недоступен'}")
    print(f"✅ WhatsApp: {'Доступен' if results['whatsapp'] else 'Недоступен'}")
    
    if results['errors']:
        print()
        print("⚠️  Ошибки:")
        for error in results['errors']:
            print(f"   - {error}")
    
    print()
    
    all_working = all([results['businesses'], results['pages']])
    if all_working:
        print("✅ Интеграция работает! Доступ к основным платформам получен.")
    else:
        print("⚠️  Некоторые платформы недоступны. Проверьте права System User.")
    
    return all_working

if __name__ == '__main__':
    test_full_access()


