#!/usr/bin/env python3
"""
WhatsApp Gate — интеграция с WhatsApp Business API через Meta.

Требует:
- Meta App с WhatsApp Product
- WhatsApp Business Account
- Phone Number подключен к WhatsApp Business
"""

import os
import json
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, List


class WhatsAppGate:
    """Универсальный интерфейс к WhatsApp Business API"""
    
    API_VERSION = 'v18.0'
    BASE_URL = f'https://graph.facebook.com/{API_VERSION}'
    
    def __init__(self, credentials_path='.gates/whatsapp/credentials.json'):
        """
        Инициализация WhatsApp Gate.
        
        credentials.json должен содержать:
        {
            "access_token": "YOUR_ACCESS_TOKEN",
            "phone_number_id": "YOUR_PHONE_NUMBER_ID",
            "business_account_id": "YOUR_BUSINESS_ACCOUNT_ID"
        }
        """
        self.credentials_path = os.path.abspath(credentials_path)
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"❌ Файл {self.credentials_path} не найден.\n"
                f"Настройте WhatsApp Business в Meta App:\n"
                f"https://developers.facebook.com/apps/ → Your App → Add Product → WhatsApp"
            )
        
        with open(self.credentials_path, 'r') as f:
            creds = json.load(f)
            self.access_token = creds['access_token']
            self.phone_number_id = creds['phone_number_id']
            self.business_account_id = creds.get('business_account_id')
    
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
        """Проверка валидности токена и получение информации о Business Account"""
        try:
            data = self._request(f'{self.business_account_id}')
            return {
                'valid': True,
                'business_account_id': data.get('id'),
                'name': data.get('name')
            }
        except:
            return {'valid': False}
    
    # === READ ===
    
    def get_messages(self, limit=25):
        """
        Получить сообщения.
        
        Note: WhatsApp API работает через webhooks (push), не polling.
        Этот метод показывает последние сообщения через Phone Number объект.
        """
        endpoint = f"{self.phone_number_id}/messages"
        data = self._request(endpoint, params={'limit': limit})
        return data.get('data', [])
    
    # === WRITE ===
    
    def send_message(self, to: str, message: str):
        """
        Отправить текстовое сообщение.
        
        Args:
            to: Номер телефона получателя (с кодом страны, без +)
                Пример: '79991234567' для России
            message: Текст сообщения
        
        Returns:
            {'message_id': ..., 'status': ...}
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': message}
        }
        
        result = self._request(endpoint, method='POST', json_data=payload)
        
        return {
            'message_id': result['messages'][0]['id'],
            'status': result['messages'][0]['message_status']
        }
    
    def send_template(self, to: str, template_name: str, language_code='ru'):
        """
        Отправить шаблонное сообщение.
        
        Args:
            to: Номер телефона
            template_name: Название утвержденного шаблона
            language_code: Код языка (ru, en, ar)
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
        
        result = self._request(endpoint, method='POST', json_data=payload)
        
        return {
            'message_id': result['messages'][0]['id'],
            'status': result['messages'][0]['message_status']
        }
    
    def send_media(self, to: str, media_type: str, media_url: str, caption: Optional[str] = None):
        """
        Отправить медиа (изображение, видео, документ).
        
        Args:
            to: Номер телефона
            media_type: 'image', 'video', 'document', 'audio'
            media_url: URL медиафайла
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
        
        result = self._request(endpoint, method='POST', json_data=payload)
        
        return {
            'message_id': result['messages'][0]['id'],
            'status': result['messages'][0]['message_status']
        }
    
    # === WEBHOOKS ===
    
    def setup_webhook(self, callback_url, verify_token):
        """
        Настройка webhook для получения сообщений.
        
        Args:
            callback_url: Публичный URL (например, Cloudflare Tunnel)
            verify_token: Любая строка для верификации
        
        Note:
            Webhooks настраиваются в Meta App Dashboard:
            App → WhatsApp → Configuration → Webhook
        """
        return {
            'callback_url': f"{callback_url}/webhook/whatsapp",
            'verify_token': verify_token,
            'note': 'Настройте в Meta App Dashboard → WhatsApp → Webhook'
        }
    
    # === EXPORT ===
    
    def export_substance(self):
        """Экспорт данных WhatsApp для Substance"""
        substance = {
            'provider': 'whatsapp_business',
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
            messages = self.get_messages(limit=50)
            substance['data']['messages'] = messages
            substance['data']['messages_count'] = len(messages)
        except Exception as e:
            substance['data']['messages_error'] = str(e)
        
        return substance


if __name__ == '__main__':
    # Тест
    try:
        gate = WhatsAppGate()
        
        print("🔐 Проверка WhatsApp Business Account...")
        account = gate.test_token()
        
        if account['valid']:
            print(f"✓ Account: {account['name']}")
            print(f"  ID: {account['business_account_id']}")
        else:
            print("❌ Токен невалиден")
        
        print("\n📊 Экспорт Substance...")
        substance = gate.export_substance()
        print(f"✓ Provider: {substance['provider']}")
        
        if 'messages_count' in substance['data']:
            print(f"  Сообщений: {substance['data']['messages_count']}")
        
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Ошибка: {e}")
