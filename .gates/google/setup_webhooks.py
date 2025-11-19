#!/usr/bin/env python3
"""
Setup Webhooks — Настройка Google Push Notifications
Gmail (Pub/Sub) + Calendar (Push Notifications)
"""

from google_gate import GoogleGate
import uuid

def setup_gmail_push():
    """
    Настроить Gmail Push Notifications через Cloud Pub/Sub
    
    Требования:
    1. В Google Cloud Console включить Cloud Pub/Sub API
    2. Создать тему (topic): projects/PROJECT_ID/topics/gmail-push
    3. Дать Gmail права на публикацию в эту тему
    """
    gate = GoogleGate()
    gmail = gate.gmail()
    
    # Получить PROJECT_ID из credentials
    # (В реальной реализации извлечь из credentials.json)
    project_id = "dela-olga-rozet"
    topic_name = f"projects/{project_id}/topics/gmail-push"
    
    print("📧 Настройка Gmail Push Notifications...")
    print(f"   Topic: {topic_name}")
    
    try:
        # Запросить watch (мониторинг почты)
        request = {
            'labelIds': ['INBOX'],
            'topicName': topic_name
        }
        
        result = gmail.users().watch(userId='me', body=request).execute()
        
        print(f"   ✓ Watch установлен")
        print(f"   ✓ History ID: {result.get('historyId')}")
        print(f"   ✓ Expiration: {result.get('expiration')}")
        print(f"   ✓ Срок действия: 7 дней (автообновление требуется)\n")
        
        return result
    
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print(f"   Убедитесь, что:")
        print(f"   1. Cloud Pub/Sub API включен")
        print(f"   2. Тема {topic_name} создана")
        print(f"   3. Gmail имеет права публикации\n")
        return None

def setup_calendar_push(webhook_url):
    """
    Настроить Calendar Push Notifications
    
    Параметры:
    - webhook_url: Публичный URL вашего webhook сервера
                   (например, https://ваш-домен.com/webhook/calendar)
    """
    gate = GoogleGate()
    calendar = gate.calendar()
    
    print("📅 Настройка Calendar Push Notifications...")
    print(f"   Webhook URL: {webhook_url}")
    
    try:
        # Создать уникальный ID канала
        channel_id = str(uuid.uuid4())
        
        # Запросить watch
        request = {
            'id': channel_id,
            'type': 'web_hook',
            'address': webhook_url
        }
        
        result = calendar.events().watch(
            calendarId='primary',
            body=request
        ).execute()
        
        print(f"   ✓ Channel создан")
        print(f"   ✓ Channel ID: {result.get('id')}")
        print(f"   ✓ Resource ID: {result.get('resourceId')}")
        print(f"   ✓ Expiration: {result.get('expiration')}")
        print(f"   ✓ Срок действия: Varies (обычно недели/месяцы)\n")
        
        # Сохранить Channel ID для возможной остановки
        with open('.calendar_channel_id', 'w') as f:
            f.write(f"{channel_id}\n{result.get('resourceId')}")
        
        return result
    
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print(f"   Убедитесь, что webhook_url публично доступен\n")
        return None

def stop_calendar_push():
    """Остановить Calendar Push Notifications"""
    gate = GoogleGate()
    calendar = gate.calendar()
    
    try:
        with open('.calendar_channel_id', 'r') as f:
            lines = f.readlines()
            channel_id = lines[0].strip()
            resource_id = lines[1].strip()
        
        calendar.channels().stop(body={
            'id': channel_id,
            'resourceId': resource_id
        }).execute()
        
        print("✓ Calendar Push остановлен")
    
    except FileNotFoundError:
        print("❌ .calendar_channel_id не найден")
    except Exception as e:
        print(f"❌ Ошибка остановки: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Setup Webhooks — Настройка Push Notifications")
    print("=" * 60)
    print()
    
    # Gmail Push
    print("ВНИМАНИЕ: Для Gmail требуется настройка Cloud Pub/Sub")
    print("См. документацию: https://developers.google.com/gmail/api/guides/push")
    print()
    
    # setup_gmail_push()
    
    # Calendar Push
    print("Для Calendar укажите публичный URL вашего webhook сервера:")
    print("Например: https://ваш-домен.com/webhook/calendar")
    print()
    
    webhook_url = input("Webhook URL (или Enter для пропуска): ").strip()
    
    if webhook_url:
        setup_calendar_push(webhook_url)
    else:
        print("Пропущено. Запустите позже с URL.")
    
    print("\n" + "=" * 60)
    print("✓ Настройка завершена")
    print("=" * 60)
