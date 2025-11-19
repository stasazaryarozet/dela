#!/usr/bin/env python3
"""
Получение OAuth токена Яндекс.Диска

Использование:
    python3 get_yandex_token.py
"""

import webbrowser
import sys

print("=" * 70)
print("ПОЛУЧЕНИЕ ТОКЕНА ЯНДЕКС.ДИСКА")
print("=" * 70)
print()

# Проверяем, передан ли ClientID как аргумент
if len(sys.argv) > 1:
    client_id = sys.argv[1]
else:
    # Интерактивный ввод
    print("У тебя уже есть приложение 'dela' на https://oauth.yandex.ru/")
    print()
    print("На странице приложения найди:")
    print("  'ClientID' - длинная строка (например: a1b2c3d4e5f6...)")
    print()
    client_id = input("Вставь ClientID сюда: ").strip()
    print()

if not client_id:
    print("❌ ClientID не указан")
    sys.exit(1)

# Формируем URL для авторизации
auth_url = (
    f"https://oauth.yandex.ru/authorize?"
    f"response_type=token&"
    f"client_id={client_id}"
)

print("=" * 70)
print("ШАГ 1: АВТОРИЗАЦИЯ")
print("=" * 70)
print()
print("Открываю браузер с URL авторизации...")
print()

# Открываем браузер
webbrowser.open(auth_url)

print(f"URL: {auth_url}")
print()
print("1. Авторизуйся в Яндексе (если нужно)")
print("2. Разреши доступ приложению")
print()
print("=" * 70)
print("ШАГ 2: СКОПИРУЙ ТОКЕН")
print("=" * 70)
print()
print("После авторизации браузер перенаправит на URL вида:")
print("  https://oauth.yandex.ru/verification_code#access_token=ТОКЕН&...")
print()
print("Скопируй ТОКЕН из этого URL (между access_token= и &)")
print()

# Интерактивный ввод токена
token = input("Вставь токен сюда: ").strip()
print()

if not token:
    print("❌ Токен не указан")
    sys.exit(1)

# Очистка токена от возможных параметров
if '&' in token:
    token = token.split('&')[0]

print("✅ Токен получен!")
print()
print("=" * 70)
print("ШАГ 3: ДОБАВЬ ТОКЕН В RAILWAY")
print("=" * 70)
print()
print("Выполни команды:")
print()
print("  cd ~/dela/telegram-bot")
print(f'  railway variables set YANDEX_DISK_TOKEN="{token}"')
print()
print("Или скопируй токен для ручного добавления через веб-интерфейс:")
print()
print(f"  {token}")
print()
print("=" * 70)
print("ГОТОВО!")
print("=" * 70)
print()
print("После добавления токена бот автоматически начнёт")
print("сохранять файлы в Яндекс.Диск:/TelegramArchive/")
print()
