#!/usr/bin/env python3
"""
Meta OAuth Authorization — "один клик"

Автоматическая авторизация для получения Access Token от Instagram/Facebook.

Использование:
    python3 authorize.py

Что происходит:
    1. Скрипт создает временный локальный сервер (http://localhost:8080)
    2. Открывает браузер с URL авторизации Meta
    3. Вы входите от аккаунта Ольги и нажимаете "Разрешить"
    4. Meta перенаправляет на localhost с токеном
    5. Скрипт автоматически получает токен и Instagram Account ID
    6. Сохраняет всё в credentials.json
    7. Готово — дальше автономно

Требования:
    - Meta App должно быть создано (https://developers.facebook.com/apps/)
    - В App Settings → Add Platform → Website → Site URL: http://localhost:8080
    - Valid OAuth Redirect URIs: http://localhost:8080/callback
"""

import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

# === КОНФИГУРАЦИЯ ===

# ВАЖНО: Замените на ваши значения из Meta App Dashboard
APP_ID = os.environ.get('META_APP_ID', '')
APP_SECRET = os.environ.get('META_APP_SECRET', '')

# Если не заданы через env, запросить интерактивно
if not APP_ID:
    print("📱 Meta App ID не найден в переменных окружения.")
    print("   Получите его: https://developers.facebook.com/apps/ → Your App → Settings → Basic\n")
    APP_ID = input("Введите App ID: ").strip()

if not APP_SECRET:
    print("\n🔐 Meta App Secret не найден в переменных окружения.")
    print("   Получите его: https://developers.facebook.com/apps/ → Your App → Settings → Basic\n")
    APP_SECRET = input("Введите App Secret: ").strip()

# OAuth настройки
REDIRECT_URI = 'http://localhost:8080/callback'
SCOPES = [
    'instagram_basic',
    'instagram_content_publish',
    'pages_read_engagement',
    'pages_show_list'
]

# Путь для сохранения credentials
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')

# Глобальная переменная для передачи токена
auth_code = None


# === OAuth CALLBACK SERVER ===

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP сервер для получения OAuth callback от Meta"""
    
    def do_GET(self):
        """Обработка GET запроса от Meta с authorization code"""
        global auth_code
        
        # Парсинг URL
        parsed = urlparse(self.path)
        
        if parsed.path == '/callback':
            # Получить code из query params
            params = parse_qs(parsed.query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                
                # Ответ пользователю
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <html>
                <head>
                    <title>Авторизация успешна</title>
                    <style>
                        body { 
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            background: white;
                            padding: 60px;
                            border-radius: 20px;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            text-align: center;
                        }
                        h1 { color: #667eea; margin-bottom: 20px; }
                        p { color: #666; font-size: 18px; }
                        .success { font-size: 72px; margin-bottom: 20px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success">✅</div>
                        <h1>Авторизация успешна!</h1>
                        <p>Можете закрыть это окно.</p>
                        <p style="font-size: 14px; color: #999; margin-top: 20px;">
                            Токен получен и сохранен автоматически.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
            else:
                # Ошибка
                error = params.get('error_description', ['Unknown error'])[0]
                
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f"""
                <html>
                <body>
                    <h1>❌ Ошибка авторизации</h1>
                    <p>{error}</p>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
        else:
            # Стартовая страница
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
            <body>
                <h1>⏳ Ожидание авторизации...</h1>
                <p>Пожалуйста, авторизуйтесь в открывшемся окне браузера.</p>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Отключить логи HTTP сервера"""
        pass


# === ОСНОВНАЯ ЛОГИКА ===

def exchange_code_for_token(code):
    """Обмен authorization code на access token"""
    url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    
    params = {
        'client_id': APP_ID,
        'client_secret': APP_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data['access_token']


def get_long_lived_token(short_token):
    """Обмен short-lived token на long-lived (60 дней)"""
    url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': APP_ID,
        'client_secret': APP_SECRET,
        'fb_exchange_token': short_token
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data['access_token']


def get_instagram_account_id(access_token):
    """Получить Instagram Business Account ID"""
    # Получить Facebook Pages
    url = 'https://graph.facebook.com/v18.0/me/accounts'
    params = {'access_token': access_token}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    pages = response.json().get('data', [])
    
    if not pages:
        raise ValueError("❌ Не найдено Facebook Pages. Убедитесь, что аккаунт связан с Page.")
    
    # Взять первую Page (обычно только одна)
    page_id = pages[0]['id']
    page_access_token = pages[0]['access_token']
    
    # Получить Instagram Business Account
    url = f'https://graph.facebook.com/v18.0/{page_id}'
    params = {
        'fields': 'instagram_business_account',
        'access_token': page_access_token
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    if 'instagram_business_account' not in data:
        raise ValueError(
            f"❌ Instagram Business Account не найден для Page '{pages[0]['name']}'.\n"
            "   Убедитесь, что Instagram-аккаунт связан с Facebook Page."
        )
    
    return data['instagram_business_account']['id']


def save_credentials(access_token, instagram_account_id):
    """Сохранить credentials в JSON"""
    credentials = {
        'access_token': access_token,
        'instagram_account_id': instagram_account_id
    }
    
    with open(CREDENTIALS_PATH, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"✅ Credentials сохранены: {CREDENTIALS_PATH}")


def main():
    """Главная функция"""
    global auth_code
    
    print("="*60)
    print("Meta OAuth Authorization — автоматическая авторизация")
    print("="*60)
    
    # Проверка App ID и Secret
    if not APP_ID or not APP_SECRET:
        print("\n❌ META_APP_ID и META_APP_SECRET должны быть заданы.")
        print("   Создайте Meta App: https://developers.facebook.com/apps/")
        return
    
    # Создать OAuth URL
    auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={','.join(SCOPES)}&"
        f"response_type=code"
    )
    
    print("\n🌐 Запуск локального сервера на http://localhost:8080...")
    
    # Запустить HTTP сервер
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    
    print("✅ Сервер запущен")
    print(f"\n🔗 Открываю браузер для авторизации...")
    print(f"   Если не открылся автоматически, перейдите по ссылке:")
    print(f"   {auth_url}\n")
    
    # Открыть браузер
    webbrowser.open(auth_url)
    
    print("⏳ Ожидание авторизации...\n")
    
    # Ждать callback (макс 5 минут)
    timeout = 300  # 5 минут
    for _ in range(timeout):
        server.handle_request()
        
        if auth_code:
            break
    
    if not auth_code:
        print("❌ Тайм-аут. Авторизация не получена за 5 минут.")
        return
    
    print("✅ Authorization code получен")
    
    try:
        print("\n🔄 Обмен code на access token...")
        short_token = exchange_code_for_token(auth_code)
        print("✅ Short-lived token получен")
        
        print("\n🔄 Обмен на long-lived token (60 дней)...")
        access_token = get_long_lived_token(short_token)
        print("✅ Long-lived token получен")
        
        print("\n🔄 Получение Instagram Business Account ID...")
        instagram_account_id = get_instagram_account_id(access_token)
        print(f"✅ Instagram Account ID: {instagram_account_id}")
        
        print("\n💾 Сохранение credentials...")
        save_credentials(access_token, instagram_account_id)
        
        print("\n" + "="*60)
        print("✅ ГОТОВО! Авторизация завершена успешно")
        print("="*60)
        print(f"\nCredentials сохранены в: {CREDENTIALS_PATH}")
        print("\nТеперь можно использовать Meta Gate:")
        print("  python3 .gates/meta_gate.py")
        print("\nИли автоматизацию продаж:")
        print("  python3 Ольга/sell_consultations.py --analyze")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\nВозможные причины:")
        print("  1. Instagram-аккаунт не связан с Facebook Page")
        print("  2. Аккаунт не Business/Creator")
        print("  3. Недостаточно прав (permissions)")


if __name__ == '__main__':
    main()
