#!/usr/bin/env python3
"""
Попытка получить доступ к WhatsApp через существующий Meta App
Использует Meta App ID из документации: 848486860991509
"""
import sys
import os
import requests
from pathlib import Path

gates_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gates_dir))

def get_whatsapp_via_meta():
    """Попытка получить доступ к WhatsApp через Meta App"""
    print("=" * 80)
    print("ПОПЫТКА ДОСТУПА К WHATSAPP ЧЕРЕЗ META APP")
    print("=" * 80)
    print()
    
    # Meta App ID из документации
    META_APP_ID = "848486860991509"
    
    # Пробуем получить доступ через Meta Gate
    try:
        from meta_gate import MetaGate
        
        print("🔐 Пробую использовать Meta Gate...")
        gate = MetaGate()
        
        if hasattr(gate, 'access_token') and gate.access_token:
            print(f"✅ Access Token найден: {gate.access_token[:20]}...")
            
            # Пробуем получить информацию о WhatsApp через Graph API
            print()
            print("📡 Проверяю доступ к WhatsApp через Graph API...")
            
            url = f"https://graph.facebook.com/v18.0/{META_APP_ID}"
            params = {
                'access_token': gate.access_token,
                'fields': 'name,whatsapp_business_accounts'
            }
            
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ App Info: {data.get('name', 'N/A')}")
                    
                    whatsapp_accounts = data.get('whatsapp_business_accounts', {})
                    if whatsapp_accounts:
                        print(f"✅ WhatsApp Business Accounts найдены!")
                        print(f"   {whatsapp_accounts}")
                        return True
                    else:
                        print("ℹ️  WhatsApp Business Accounts не настроены")
                else:
                    print(f"⚠️  Ошибка API: {response.status_code}")
                    print(f"   {response.text[:200]}")
            except Exception as e:
                print(f"❌ Ошибка запроса: {e}")
        else:
            print("⚠️  Access Token не найден в Meta Gate")
            
    except FileNotFoundError:
        print("⚠️  Meta Gate credentials не найдены")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Пробуем найти credentials в других местах
    print()
    print("🔍 Ищу credentials в других местах...")
    
    possible_locations = [
        gates_dir / 'meta' / 'credentials.json',
        gates_dir / 'whatsapp' / 'credentials.json',
        gates_dir / 'facebook_credentials.json',
    ]
    
    for loc in possible_locations:
        if loc.exists():
            print(f"✅ Найден файл: {loc}")
            try:
                import json
                with open(loc, 'r') as f:
                    creds = json.load(f)
                    if 'access_token' in creds:
                        print(f"   Access Token найден: {creds['access_token'][:20]}...")
                        # Пробуем использовать для WhatsApp
                        return try_whatsapp_api(creds['access_token'], META_APP_ID)
            except Exception as e:
                print(f"   ⚠️  Ошибка чтения: {e}")
    
    print("❌ Credentials не найдены")
    return False

def try_whatsapp_api(access_token, app_id):
    """Попытка использовать access token для WhatsApp API"""
    print()
    print("📡 Пробую получить доступ к WhatsApp Business API...")
    
    # Пробуем получить список WhatsApp Business Accounts
    url = f"https://graph.facebook.com/v18.0/{app_id}/whatsapp_business_accounts"
    params = {'access_token': access_token}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            if accounts:
                print(f"✅ Найдено WhatsApp Business Accounts: {len(accounts)}")
                for acc in accounts:
                    print(f"   ID: {acc.get('id')}")
                    print(f"   Name: {acc.get('name', 'N/A')}")
                return True
            else:
                print("ℹ️  WhatsApp Business Accounts не найдены")
        else:
            print(f"⚠️  Ошибка: {response.status_code}")
            print(f"   {response.text[:200]}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    return False

if __name__ == '__main__':
    success = get_whatsapp_via_meta()
    sys.exit(0 if success else 1)


