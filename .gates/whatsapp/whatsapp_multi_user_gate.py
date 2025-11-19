#!/usr/bin/env python3
"""
WhatsApp Multi-User Gate — глубокий доступ для Azarya и Olga

Принципы:
- Глубоко: полный доступ ко всем возможностям API
- Доверительно: изолированные credentials для каждого пользователя
- Вечно: автоматическое обновление токенов, долгосрочная совместимость
"""
import os
import json
import pickle
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Union
from pathlib import Path

# Базовый Gate доступен через относительный импорт
# Используем собственную реализацию для multi-user поддержки


class WhatsAppMultiUserGate:
    """
    Multi-user WhatsApp Gate для глубокой интеграции
    
    Поддерживает:
    - Azarya (azarya)
    - Olga (olga)
    - Легко расширяется для новых пользователей
    """
    
    API_VERSION = 'v18.0'
    BASE_URL = f'https://graph.facebook.com/{API_VERSION}'
    
    def __init__(self, user: str = 'azarya'):
        """
        Инициализация WhatsApp Gate для конкретного пользователя.
        
        Args:
            user: 'azarya' или 'olga'
        """
        self.user = user
        # Путь к директории whatsapp (где находится этот файл)
        self.whatsapp_dir = Path(__file__).parent
        self.credentials_dir = self.whatsapp_dir / 'credentials'
        self.sessions_dir = self.whatsapp_dir / 'sessions'
        
        # Создаем директории если их нет
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.credentials_path = self.credentials_dir / f'{user}_credentials.json'
        self.token_path = self.sessions_dir / f'{user}_token.pickle'
        
        # Загружаем credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Загрузка credentials для пользователя"""
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"❌ Credentials для пользователя '{self.user}' не найдены.\n"
                f"Создайте файл: {self.credentials_path}\n"
                f"Используйте скрипт: .gates/whatsapp/scripts/setup_{self.user}_whatsapp.py"
            )
        
        with open(self.credentials_path, 'r') as f:
            creds = json.load(f)
            self.access_token = creds['access_token']
            self.phone_number_id = creds['phone_number_id']
            self.business_account_id = creds.get('business_account_id')
            self.webhook_verify_token = creds.get('webhook_verify_token', f'verify_token_{self.user}')
    
    def _request(self, endpoint, params=None, method='GET', data=None, json_data=None):
        """Универсальный запрос к WhatsApp API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            if json_data:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=json_data)
            else:
                response = requests.post(url, params=params, data=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, params=params, headers=headers)
        
        response.raise_for_status()
        return response.json()
    
    # === AUTH ===
    
    def test_token(self):
        """Проверка валидности токена"""
        try:
            data = self._request(f'{self.business_account_id}')
            return {
                'valid': True,
                'user': self.user,
                'business_account_id': data.get('id'),
                'name': data.get('name')
            }
        except Exception as e:
            return {
                'valid': False,
                'user': self.user,
                'error': str(e)
            }
    
    def refresh_token(self):
        """
        Обновление токена (если поддерживается API).
        
        Note: WhatsApp Business API использует долгоживущие токены,
        но может потребоваться обновление через Meta App Dashboard.
        """
        # Для WhatsApp Business API токены обычно долгоживущие
        # Обновление может потребоваться только при смене прав доступа
        return {
            'user': self.user,
            'status': 'token_refresh_not_needed',
            'note': 'WhatsApp Business API использует долгоживущие токены'
        }
    
    # === READ ===
    
    def get_messages(self, limit: int = 25, filters: Optional[Dict] = None):
        """
        Получить сообщения.
        
        Note: WhatsApp API работает через webhooks (push), не polling.
        Этот метод показывает последние сообщения через Phone Number объект.
        """
        endpoint = f"{self.phone_number_id}/messages"
        params = {'limit': limit}
        if filters:
            params.update(filters)
        
        try:
            data = self._request(endpoint, params=params)
            return {
                'user': self.user,
                'messages': data.get('data', []),
                'count': len(data.get('data', []))
            }
        except Exception as e:
            return {
                'user': self.user,
                'error': str(e),
                'messages': []
            }
    
    def get_contacts(self, limit: int = 100):
        """Получить контакты из WhatsApp Business"""
        # WhatsApp Business API не предоставляет прямой доступ к контактам
        # Контакты извлекаются из сообщений
        return {
            'user': self.user,
            'note': 'Контакты извлекаются из истории сообщений',
            'contacts': []
        }
    
    # === WRITE ===
    
    def send_message(self, to: str, message: str):
        """
        Отправить текстовое сообщение.
        
        Args:
            to: Номер телефона получателя (с кодом страны, без +)
                Пример: '79991234567' для России
            message: Текст сообщения
        
        Returns:
            {'message_id': ..., 'status': ..., 'user': ...}
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': message}
        }
        
        try:
            result = self._request(endpoint, method='POST', json_data=payload)
            return {
                'user': self.user,
                'message_id': result['messages'][0]['id'],
                'status': result['messages'][0]['message_status'],
                'to': to
            }
        except Exception as e:
            return {
                'user': self.user,
                'error': str(e),
                'to': to
            }
    
    def send_template(self, to: str, template_name: str, language_code: str = 'ru', parameters: Optional[List] = None):
        """
        Отправить шаблонное сообщение.
        
        Args:
            to: Номер телефона
            template_name: Название утвержденного шаблона
            language_code: Код языка (ru, en, ar)
            parameters: Параметры шаблона (опционально)
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language_code}
            }
        }
        
        if parameters:
            payload['template']['components'] = [{
                'type': 'body',
                'parameters': parameters
            }]
        
        try:
            result = self._request(endpoint, method='POST', json_data=payload)
            return {
                'user': self.user,
                'message_id': result['messages'][0]['id'],
                'status': result['messages'][0]['message_status'],
                'to': to,
                'template': template_name
            }
        except Exception as e:
            return {
                'user': self.user,
                'error': str(e),
                'to': to
            }
    
    def send_media(self, to: str, media_type: str, media_url: str, caption: Optional[str] = None):
        """
        Отправить медиа (изображение, видео, документ).
        
        Args:
            to: Номер телефона
            media_type: 'image', 'video', 'document', 'audio'
            media_url: URL медиафайла (публично доступный)
            caption: Подпись (опционально)
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': media_type,
            media_type: {'link': media_url}
        }
        
        if caption and media_type in ['image', 'video', 'document']:
            payload[media_type]['caption'] = caption
        
        try:
            result = self._request(endpoint, method='POST', json_data=payload)
            return {
                'user': self.user,
                'message_id': result['messages'][0]['id'],
                'status': result['messages'][0]['message_status'],
                'to': to,
                'media_type': media_type
            }
        except Exception as e:
            return {
                'user': self.user,
                'error': str(e),
                'to': to
            }
    
    # === WEBHOOKS ===
    
    def setup_webhook(self, callback_url: str, verify_token: Optional[str] = None):
        """
        Настройка webhook для получения сообщений.
        
        Args:
            callback_url: Публичный URL (например, Cloudflare Tunnel)
            verify_token: Токен для верификации (по умолчанию из credentials)
        
        Note:
            Webhooks настраиваются в Meta App Dashboard:
            App → WhatsApp → Configuration → Webhook
        """
        token = verify_token or self.webhook_verify_token
        
        return {
            'user': self.user,
            'callback_url': f"{callback_url}/webhook/whatsapp/{self.user}",
            'verify_token': token,
            'note': f'Настройте в Meta App Dashboard → WhatsApp → Webhook для пользователя {self.user}'
        }
    
    # === EXPORT ===
    
    def export_substance(self, messages_limit: int = 50):
        """
        Экспорт данных WhatsApp для Substance.
        
        Args:
            messages_limit: Максимальное количество сообщений для экспорта
        
        Returns:
            Substance формат для интеграции с проектом
        """
        substance = {
            'provider': 'whatsapp_business',
            'user': self.user,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {}
        }
        
        # Информация о Business Account
        try:
            account_info = self.test_token()
            substance['data']['account'] = account_info
        except Exception as e:
            substance['data']['account_error'] = str(e)
        
        # Последние сообщения
        try:
            messages_data = self.get_messages(limit=messages_limit)
            substance['data']['messages'] = messages_data.get('messages', [])
            substance['data']['messages_count'] = messages_data.get('count', 0)
        except Exception as e:
            substance['data']['messages_error'] = str(e)
        
        return substance
    
    # === UTILITIES ===
    
    def get_phone_number_info(self):
        """Получить информацию о номере телефона"""
        try:
            data = self._request(f'{self.phone_number_id}')
            return {
                'user': self.user,
                'phone_number_id': data.get('id'),
                'display_phone_number': data.get('display_phone_number'),
                'verified_name': data.get('verified_name'),
                'quality_rating': data.get('quality_rating')
            }
        except Exception as e:
            return {
                'user': self.user,
                'error': str(e)
            }


# === FACTORY FUNCTION ===

def get_whatsapp_gate(user: str = 'azarya') -> WhatsAppMultiUserGate:
    """
    Factory функция для получения WhatsApp Gate для пользователя.
    
    Args:
        user: 'azarya' или 'olga'
    
    Returns:
        WhatsAppMultiUserGate instance
    """
    return WhatsAppMultiUserGate(user=user)


if __name__ == '__main__':
    # Тест для обоих пользователей
    print("=" * 80)
    print("WHATSAPP MULTI-USER GATE — ТЕСТ")
    print("=" * 80)
    print()
    
    for user in ['azarya', 'olga']:
        try:
            print(f"🔐 Тест для пользователя: {user}")
            gate = WhatsAppMultiUserGate(user=user)
            
            account = gate.test_token()
            if account['valid']:
                print(f"  ✅ Account: {account.get('name', 'N/A')}")
                print(f"  ✅ ID: {account.get('business_account_id', 'N/A')}")
            else:
                print(f"  ❌ Токен невалиден: {account.get('error', 'Unknown error')}")
            
            phone_info = gate.get_phone_number_info()
            if 'error' not in phone_info:
                print(f"  ✅ Phone: {phone_info.get('display_phone_number', 'N/A')}")
            
            print()
            
        except FileNotFoundError as e:
            print(f"  ⚠️  Credentials не найдены: {e}")
            print()
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            print()

