#!/usr/bin/env python3
"""
Тест доступа к Instagram через Meta API
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

def load_user_token():
    """Загрузить User Access Token из credentials"""
    credentials_path = meta_dir / 'credentials.json'
    if credentials_path.exists():
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
            return creds.get('access_token')
    return None

def test_instagram_access():
    """Тест доступа к Instagram"""
    print("=" * 80)
    print("ТЕСТ ДОСТУПА К INSTAGRAM")
    print("=" * 80)
    print()
    
    # Пробуем System User Token сначала
    token = load_system_user_token()
    token_type = "System User Token"
    
    # Если нет System User Token, используем User Token
    if not token:
        token = load_user_token()
        token_type = "User Access Token"
    
    if not token:
        print("❌ Токен не найден")
        print("   Создайте System User Token: python3 .gates/meta/save_system_user_token.py")
        return False
    
    print(f"✅ Используется: {token_type}")
    print()
    
    # Метод 1: Через Facebook Pages
    print("📡 Метод 1: Получение Instagram через Facebook Pages...")
    
    try:
        pages_response = requests.get(
            'https://graph.facebook.com/v18.0/me/accounts',
            params={
                'access_token': token,
                'fields': 'id,name,instagram_business_account'
            }
        )
        
        if pages_response.status_code == 200:
            pages = pages_response.json().get('data', [])
            print(f"   ✅ Найдено страниц: {len(pages)}")
            
            instagram_accounts = []
            for page in pages:
                page_id = page.get('id')
                page_name = page.get('name', 'Unknown')
                instagram_account = page.get('instagram_business_account')
                
                if instagram_account:
                    instagram_id = instagram_account.get('id')
                    print(f"   ✅ Instagram найден для страницы '{page_name}':")
                    print(f"      Page ID: {page_id}")
                    print(f"      Instagram Business Account ID: {instagram_id}")
                    
                    # Получаем информацию об Instagram аккаунте
                    try:
                        insta_info_response = requests.get(
                            f'https://graph.facebook.com/v18.0/{instagram_id}',
                            params={
                                'access_token': token,
                                'fields': 'username,name,profile_picture_url'
                            }
                        )
                        
                        if insta_info_response.status_code == 200:
                            insta_info = insta_info_response.json()
                            print(f"      Username: {insta_info.get('username', 'N/A')}")
                            print(f"      Name: {insta_info.get('name', 'N/A')}")
                            instagram_accounts.append({
                                'page_id': page_id,
                                'page_name': page_name,
                                'instagram_id': instagram_id,
                                'username': insta_info.get('username'),
                                'name': insta_info.get('name')
                            })
                        else:
                            print(f"      ⚠️  Не удалось получить информацию: {insta_info_response.status_code}")
                    except Exception as e:
                        print(f"      ⚠️  Ошибка получения информации: {e}")
                else:
                    print(f"   ℹ️  Instagram не связан со страницей '{page_name}'")
            
            if instagram_accounts:
                print()
                print("=" * 80)
                print("✅ INSTAGRAM ДОСТУПЕН")
                print("=" * 80)
                print()
                print(f"Найдено Instagram аккаунтов: {len(instagram_accounts)}")
                for i, acc in enumerate(instagram_accounts, 1):
                    print(f"\n{i}. {acc.get('username', 'N/A')}")
                    print(f"   Name: {acc.get('name', 'N/A')}")
                    print(f"   Instagram ID: {acc.get('instagram_id')}")
                    print(f"   Связан с Page: {acc.get('page_name')} (ID: {acc.get('page_id')})")
                return True
            else:
                print()
                print("⚠️  Instagram аккаунты не найдены")
                print()
                print("Возможные причины:")
                print("  1. Instagram не связан с Facebook Page")
                print("  2. Instagram не является Business/Creator аккаунтом")
                print("  3. Права не назначены через System User")
                print()
                print("Решение:")
                print("  1. Свяжите Instagram с Facebook Page в Page Settings")
                print("  2. Убедитесь что Instagram Professional аккаунт")
                print("  3. Назначьте права через System User в Business Settings")
                return False
        else:
            print(f"   ❌ Ошибка получения страниц: {pages_response.status_code}")
            print(f"   Ответ: {pages_response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_instagram_access()


