#!/usr/bin/env python3
"""
Meta Gate — доступ к Instagram и Facebook через Meta Graph API.

Требует:
- pip install requests
- Приложение в https://developers.facebook.com
- Access Token с правами: instagram_basic, instagram_content_publish, pages_read_engagement
"""

import os
import json
import requests
from datetime import datetime, timezone


class MetaGate:
    """Универсальный интерфейс к Meta (Instagram + Facebook)"""
    
    API_VERSION = 'v18.0'
    BASE_URL = f'https://graph.facebook.com/{API_VERSION}'
    
    def __init__(self, credentials_path='.gates/meta/credentials.json'):
        """
        Инициализация Meta Gate.
        
        credentials.json должен содержать:
        {
            "access_token": "YOUR_ACCESS_TOKEN",
            "instagram_account_id": "INSTAGRAM_BUSINESS_ACCOUNT_ID"
        }
        """
        self.credentials_path = os.path.abspath(credentials_path)
        self.credentials_dir = os.path.dirname(self.credentials_path)
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"❌ Файл {self.credentials_path} не найден.\n"
                f"Создайте приложение на https://developers.facebook.com\n"
                f"и сохраните Access Token в этот файл."
            )
        
        with open(self.credentials_path, 'r') as f:
            creds = json.load(f)
            self.access_token = creds['access_token']
            self.instagram_account_id = creds.get('instagram_account_id')
    
    def _request(self, endpoint, params=None, method='GET', data=None):
        """Универсальный запрос к Meta Graph API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        if method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'POST':
            response = requests.post(url, params=params, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, params=params)
        
        response.raise_for_status()
        return response.json()
    
    # === AUTH ===
    
    def test_token(self):
        """Проверка валидности токена"""
        data = self._request('me', params={'fields': 'id,name'})
        return {
            'valid': True,
            'user_id': data['id'],
            'name': data['name']
        }
    
    # === READ (Instagram) ===
    
    def get_instagram_media(self, limit=25, fields=None):
        """
        Получить медиа из Instagram.
        
        fields: список полей (по умолчанию: id, caption, media_type, media_url, timestamp, like_count, comments_count)
        """
        if not self.instagram_account_id:
            raise ValueError("❌ Instagram Account ID не указан в credentials.json")
        
        if fields is None:
            fields = 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count'
        
        endpoint = f"{self.instagram_account_id}/media"
        data = self._request(endpoint, params={'fields': fields, 'limit': limit})
        
        return data.get('data', [])
    
    def get_instagram_insights(self, metric='impressions,reach,profile_views'):
        """
        Получить метрики аккаунта Instagram.
        
        metric: impressions, reach, profile_views, follower_count, etc.
        """
        if not self.instagram_account_id:
            raise ValueError("❌ Instagram Account ID не указан в credentials.json")
        
        endpoint = f"{self.instagram_account_id}/insights"
        data = self._request(endpoint, params={'metric': metric})
        
        return data.get('data', [])
    
    def get_instagram_comments(self, media_id):
        """Получить комментарии к посту"""
        endpoint = f"{media_id}/comments"
        data = self._request(endpoint, params={'fields': 'id,text,username,timestamp'})
        
        return data.get('data', [])
    
    # === WRITE (Instagram) ===
    
    def create_instagram_post(self, image_url, caption):
        """
        Создать пост в Instagram (2-этапный процесс).
        
        1. Создать контейнер
        2. Опубликовать контейнер
        """
        if not self.instagram_account_id:
            raise ValueError("❌ Instagram Account ID не указан в credentials.json")
        
        # Шаг 1: Создать контейнер
        endpoint = f"{self.instagram_account_id}/media"
        container = self._request(
            endpoint,
            method='POST',
            params={
                'image_url': image_url,
                'caption': caption
            }
        )
        
        container_id = container['id']
        
        # Шаг 2: Опубликовать
        publish_endpoint = f"{self.instagram_account_id}/media_publish"
        result = self._request(
            publish_endpoint,
            method='POST',
            params={'creation_id': container_id}
        )
        
        return result
    
    def reply_to_comment(self, comment_id, message):
        """Ответить на комментарий"""
        endpoint = f"{comment_id}/replies"
        return self._request(endpoint, method='POST', params={'message': message})
    
    # === WEBHOOKS ===
    
    def setup_webhook(self, callback_url, verify_token, fields='feed,comments,mentions'):
        """
        Настройка webhook для Instagram.
        
        Требует настройки в Meta App Dashboard:
        - Webhooks → Instagram → Subscribe
        - Callback URL: ваш публичный URL
        - Verify Token: любая строка (сохраните её)
        """
        # Webhooks настраиваются через Meta App Dashboard, но можно проверить подписки
        endpoint = f"{self.instagram_account_id}/subscribed_apps"
        return self._request(endpoint)
    
    # === EXPORT ===
    
    def export_substance(self, media_limit=50):
        """
        Экспорт всех данных Instagram для Substance.
        
        Включает:
        - Последние посты
        - Метрики аккаунта
        - Комментарии к постам
        """
        substance = {
            'provider': 'meta_instagram',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'account_id': self.instagram_account_id,
            'data': {}
        }
        
        # Посты
        try:
            media = self.get_instagram_media(limit=media_limit)
            substance['data']['media'] = media
            substance['data']['media_count'] = len(media)
        except Exception as e:
            substance['data']['media_error'] = str(e)
        
        # Метрики
        try:
            insights = self.get_instagram_insights()
            substance['data']['insights'] = insights
        except Exception as e:
            substance['data']['insights_error'] = str(e)
        
        # Комментарии к последним 10 постам
        comments_all = []
        if 'media' in substance['data']:
            for post in substance['data']['media'][:10]:
                try:
                    comments = self.get_instagram_comments(post['id'])
                    comments_all.extend(comments)
                except:
                    pass
        
        substance['data']['recent_comments'] = comments_all
        substance['data']['comments_count'] = len(comments_all)
        
        return substance


if __name__ == '__main__':
    # Тест
    try:
        gate = MetaGate()
        
        print("🔐 Проверка токена...")
        user = gate.test_token()
        print(f"✓ Авторизован: {user['name']} (ID: {user['user_id']})")
        
        print("\n📸 Получение постов Instagram...")
        media = gate.get_instagram_media(limit=5)
        print(f"✓ Получено постов: {len(media)}")
        
        if media:
            print(f"\nПоследний пост:")
            print(f"  Caption: {media[0].get('caption', 'N/A')[:100]}...")
            print(f"  Likes: {media[0].get('like_count', 0)}")
            print(f"  Comments: {media[0].get('comments_count', 0)}")
        
        print("\n📊 Экспорт Substance...")
        substance = gate.export_substance(media_limit=10)
        print(f"✓ Экспортировано:")
        print(f"  Постов: {substance['data'].get('media_count', 0)}")
        print(f"  Комментариев: {substance['data'].get('comments_count', 0)}")
        
    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Ошибка: {e}")
