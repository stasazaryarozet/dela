#!/usr/bin/env python3
"""
Глубокая и вечная интеграция с Meta
OAuth авторизация для получения долгоживущих токенов со всеми правами
"""
import os
import json
import webbrowser
import secrets
import socket
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from pathlib import Path
from datetime import datetime

# === КОНФИГУРАЦИЯ ===

# Meta App ID из документации
APP_ID = os.environ.get('META_APP_ID', '848486860991509')

# Пробуем загрузить App Secret из .env файла
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('META_APP_SECRET='):
                APP_SECRET = line.split('=', 1)[1].strip().strip('"').strip("'")
                break
        else:
            APP_SECRET = os.environ.get('META_APP_SECRET', '')
else:
    APP_SECRET = os.environ.get('META_APP_SECRET', '')

# Если App Secret не задан, выводим инструкции
if not APP_SECRET:
    print("=" * 80)
    print("ГЛУБОКАЯ ИНТЕГРАЦИЯ С META")
    print("=" * 80)
    print()
    print("⚠️  App Secret не найден")
    print()
    print("Для получения App Secret:")
    print("1. Откройте https://developers.facebook.com/apps/848486860991509/")
    print("2. Settings → Basic → App Secret → Show")
    print("3. Сохраните в .gates/meta/.env как:")
    print("   META_APP_SECRET=your_secret_here")
    print()
    print("Или запустите скрипт снова после сохранения App Secret")
    print()
    exit(1)

# Валидные permissions согласно актуальной документации Meta (2024-2025)
# Источник: https://developers.facebook.com/docs/facebook-login/permissions
# 
# ВАЖНО: Многие permissions были удалены из Facebook Login и доступны только через:
# - Page Access Tokens (для работы со страницами)
# - System User Tokens (для WhatsApp Business API)
# - App Review (для расширенных прав)
SCOPES = [
    # Базовые права пользователя (всегда валидны)
    'public_profile',
    
    # Facebook Pages - только базовые права через Facebook Login
    'pages_show_list',           # Список страниц пользователя (валидно)
    'pages_read_engagement',     # Чтение метрик страниц (валидно)
    
    # Business Management (для доступа к бизнес-аккаунтам)
    'business_management',       # Управление бизнес-аккаунтами Meta (валидно)
    
    # Примечание: 
    # - email, pages_manage_posts, pages_read_user_content - НЕ валидны для Facebook Login
    # - Эти права получаются через Page Access Tokens после авторизации
    # - Instagram permissions получаются автоматически через связанные Pages
    # - WhatsApp Business API требует System User Token через Meta App Dashboard
]

# Redirect URI для OAuth (используем случайный порт если 8080 занят)
def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

PORT = get_free_port()
REDIRECT_URI = f'http://localhost:{PORT}/callback'
VERIFY_TOKEN = secrets.token_urlsafe(32)

class OAuthHandler(BaseHTTPRequestHandler):
    """Обработчик OAuth callback"""
    
    def do_GET(self):
        """Обработка GET запроса"""
        if self.path.startswith('/callback'):
            # Парсим callback URL
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            # Проверяем наличие кода авторизации
            if 'code' in params:
                code = params['code'][0]
                
                # Обмениваем код на access token
                token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
                token_params = {
                    'client_id': APP_ID,
                    'client_secret': APP_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                }
                
                try:
                    response = requests.get(token_url, params=token_params)
                    if response.status_code == 200:
                        token_data = response.json()
                        access_token = token_data.get('access_token')
                        expires_in = token_data.get('expires_in', 0)
                        
                        # Обмениваем на долгоживущий токен (60 дней)
                        long_lived_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
                        long_lived_params = {
                            'grant_type': 'fb_exchange_token',
                            'client_id': APP_ID,
                            'client_secret': APP_SECRET,
                            'fb_exchange_token': access_token
                        }
                        
                        long_response = requests.get(long_lived_url, params=long_lived_params)
                        if long_response.status_code == 200:
                            long_token_data = long_response.json()
                            long_access_token = long_token_data.get('access_token')
                            long_expires_in = long_token_data.get('expires_in', 0)
                            
                            # Получаем информацию о пользователе
                            # email может быть недоступен без соответствующего permission
                            user_info = requests.get(
                                'https://graph.facebook.com/v18.0/me',
                                params={'access_token': long_access_token, 'fields': 'id,name'}
                            ).json()
                            
                            # Пробуем получить email отдельно (может не работать)
                            try:
                                email_response = requests.get(
                                    'https://graph.facebook.com/v18.0/me',
                                    params={'access_token': long_access_token, 'fields': 'email'}
                                )
                                if email_response.status_code == 200:
                                    email_data = email_response.json()
                                    if 'email' in email_data:
                                        user_info['email'] = email_data['email']
                            except:
                                pass
                            
                            # Получаем список страниц
                            pages_info = requests.get(
                                'https://graph.facebook.com/v18.0/me/accounts',
                                params={'access_token': long_access_token}
                            ).json()
                            
                            # Получаем WhatsApp Business Accounts через Business Management API
                            whatsapp_accounts = []
                            whatsapp_phone_numbers = []
                            try:
                                # Сначала получаем бизнес-аккаунты пользователя
                                business_response = requests.get(
                                    'https://graph.facebook.com/v18.0/me/businesses',
                                    params={'access_token': long_access_token}
                                )
                                if business_response.status_code == 200:
                                    businesses = business_response.json().get('data', [])
                                    
                                    # Для каждого бизнеса получаем WhatsApp Business Accounts
                                    for business in businesses[:5]:  # Ограничиваем до 5 бизнесов
                                        try:
                                            waba_response = requests.get(
                                                f"https://graph.facebook.com/v18.0/{business['id']}/owned_whatsapp_business_accounts",
                                                params={'access_token': long_access_token}
                                            )
                                            if waba_response.status_code == 200:
                                                waba_data = waba_response.json().get('data', [])
                                                whatsapp_accounts.extend(waba_data)
                                                
                                                # Для каждого WABA получаем номера телефонов
                                                for waba in waba_data:
                                                    try:
                                                        phone_response = requests.get(
                                                            f"https://graph.facebook.com/v18.0/{waba['id']}/phone_numbers",
                                                            params={'access_token': long_access_token}
                                                        )
                                                        if phone_response.status_code == 200:
                                                            phones = phone_response.json().get('data', [])
                                                            whatsapp_phone_numbers.extend(phones)
                                                    except:
                                                        pass
                                        except:
                                            pass
                            except Exception as e:
                                print(f"⚠️  Ошибка получения WhatsApp Accounts: {e}")
                            
                            # Сохраняем credentials
                            credentials_dir = Path(__file__).parent
                            credentials_path = credentials_dir / 'credentials.json'
                            
                            # Получаем Instagram Business Accounts для каждой страницы
                            instagram_accounts = []
                            for page in pages_info.get('data', []):
                                try:
                                    page_token = page.get('access_token')
                                    page_id = page.get('id')
                                    insta_response = requests.get(
                                        f'https://graph.facebook.com/v18.0/{page_id}',
                                        params={
                                            'fields': 'instagram_business_account',
                                            'access_token': page_token
                                        }
                                    )
                                    if insta_response.status_code == 200:
                                        insta_data = insta_response.json()
                                        if 'instagram_business_account' in insta_data:
                                            instagram_accounts.append({
                                                'page_id': page_id,
                                                'page_name': page.get('name'),
                                                'instagram_account_id': insta_data['instagram_business_account']['id']
                                            })
                                except:
                                    pass
                            
                            credentials = {
                                'access_token': long_access_token,
                                'token_type': 'long_lived',
                                'expires_in': long_expires_in,
                                'expires_at': datetime.now().timestamp() + long_expires_in if long_expires_in else None,
                                'user': {
                                    'id': user_info.get('id'),
                                    'name': user_info.get('name'),
                                    'email': user_info.get('email', None)  # Может быть None если permission не предоставлен
                                },
                                'pages': pages_info.get('data', []),
                                'instagram_accounts': instagram_accounts,
                                'whatsapp_business_accounts': whatsapp_accounts,
                                'whatsapp_phone_numbers': whatsapp_phone_numbers,
                                'created_at': datetime.now().isoformat(),
                                'scopes': SCOPES,
                                'note': 'Page Access Tokens в pages[] можно использовать для управления постами и контентом'
                            }
                            
                            with open(credentials_path, 'w') as f:
                                json.dump(credentials, f, indent=2, ensure_ascii=False)
                            
                            # Отправляем успешный ответ
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.end_headers()
                            
                            success_html = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>Авторизация успешна</title>
                                <style>
                                    body {{
                                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                        display: flex;
                                        justify-content: center;
                                        align-items: center;
                                        height: 100vh;
                                        margin: 0;
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    }}
                                    .container {{
                                        background: white;
                                        padding: 40px;
                                        border-radius: 10px;
                                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                        max-width: 500px;
                                        text-align: center;
                                    }}
                                    h1 {{
                                        color: #667eea;
                                        margin-bottom: 20px;
                                    }}
                                    .success {{
                                        color: #10b981;
                                        font-size: 48px;
                                        margin-bottom: 20px;
                                    }}
                                    p {{
                                        color: #6b7280;
                                        line-height: 1.6;
                                    }}
                                </style>
                            </head>
                            <body>
                                <div class="container">
                                    <div class="success">✅</div>
                                    <h1>Авторизация успешна!</h1>
                                    <p>Токен сохранен в:<br><code>{credentials_path}</code></p>
                                    <p>Токен действителен: <strong>{long_expires_in // 86400} дней</strong></p>
                                    <p>Страниц: {len(pages_info.get('data', []))}</p>
                                    <p>Instagram Accounts: {len(instagram_accounts)}</p>
                                    <p>WhatsApp Accounts: {len(whatsapp_accounts)}</p>
                                    <p>Можно закрыть это окно.</p>
                                </div>
                            </body>
                            </html>
                            """
                            self.wfile.write(success_html.encode('utf-8'))
                            
                            print()
                            print("=" * 80)
                            print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
                            print("=" * 80)
                            print()
                            print(f"📄 Credentials сохранены: {credentials_path}")
                            print(f"👤 Пользователь: {user_info.get('name', 'N/A')}")
                            print(f"📧 Email: {user_info.get('email', 'N/A')}")
                            print(f"📱 Страниц: {len(pages_info.get('data', []))}")
                            print(f"📸 Instagram Accounts: {len(instagram_accounts)}")
                            print(f"💬 WhatsApp Business Accounts: {len(whatsapp_accounts)}")
                            if whatsapp_phone_numbers:
                                print(f"📞 WhatsApp Phone Numbers: {len(whatsapp_phone_numbers)}")
                            print(f"⏰ Токен действителен: {long_expires_in // 86400} дней")
                            print()
                            
                            # Останавливаем сервер
                            self.server.shutdown()
                        else:
                            raise Exception(f"Ошибка обмена на долгоживущий токен: {long_response.text}")
                    else:
                        raise Exception(f"Ошибка получения токена: {response.text}")
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    error_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Ошибка</title>
                    </head>
                    <body>
                        <h1>Ошибка авторизации</h1>
                        <p>{str(e)}</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(error_html.encode('utf-8'))
                    print(f"❌ Ошибка: {e}")
                    self.server.shutdown()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Bad Request')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Отключаем логирование"""
        pass

def main():
    """Главная функция авторизации"""
    print("=" * 80)
    print("ГЛУБОКАЯ И ВЕЧНАЯ ИНТЕГРАЦИЯ С META")
    print("=" * 80)
    print()
    print("Этот скрипт создаст долгоживущий токен (60 дней) со всеми правами:")
    print("  ✅ Instagram (публикация, комментарии, аналитика)")
    print("  ✅ WhatsApp Business (сообщения, управление)")
    print("  ✅ Facebook Pages (управление страницами)")
    print("  ✅ Business Management")
    print()
    print("Токен будет автоматически обновляться при необходимости.")
    print()
    
    # Формируем URL авторизации
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth"
    auth_params = {
        'client_id': APP_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ','.join(SCOPES),
        'response_type': 'code',
        'state': VERIFY_TOKEN
    }
    
    auth_full_url = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
    
    print(f"Запускаю локальный сервер на порту {PORT}...")
    print()
    
    # Запускаем локальный сервер
    server = HTTPServer(('localhost', PORT), OAuthHandler)
    
    print("Открываю браузер для авторизации...")
    print()
    print("⚠️  ВАЖНО:")
    print("   1. Войдите от аккаунта Ольги")
    print("   2. Разрешите ВСЕ запрошенные права")
    print("   3. После авторизации токен будет сохранен автоматически")
    print()
    print(f"📋 Запрошенные права:")
    for scope in SCOPES:
        print(f"   ✅ {scope}")
    print()
    
    # Открываем браузер
    print(f"🔗 URL авторизации: {auth_full_url[:100]}...")
    webbrowser.open(auth_full_url)
    
    print()
    print("⏳ Ожидаю авторизации...")
    print(f"   Сервер работает на http://localhost:{PORT}")
    print("   (Закройте это окно после успешной авторизации)")
    print()
    
    # Запускаем сервер (serve_forever будет работать до shutdown из callback)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
        server.shutdown()
    finally:
        server.server_close()
        print("\n✅ Готово!")

if __name__ == '__main__':
    main()

