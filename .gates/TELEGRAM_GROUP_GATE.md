# Telegram Group Gate

**Gate для чтения истории Telegram группы через Telethon (User API)**

---

## Архитектура

### Отличия от других Telegram Gates

| Gate | API | Назначение | История |
|------|-----|------------|---------|
| `telegram_remote_gate.py` | Bot API | Публикация сообщений | ❌ Только новые |
| `telegram_archive_gate.py` | Bot API | Доступ к архиву бота | ✅ Из архива |
| `telegram_group_gate.py` | User API (Telethon) | Чтение истории группы | ✅ Полная история |

### Принцип работы

```
TelegramGroupGate
  ↓
Telethon (User API)
  ↓
Авторизация пользователя (один раз)
  ↓
Чтение истории группы
  ↓
Экспорт Substance
```

---

## Установка

### 1. Установка зависимостей

```bash
pip install telethon
```

### 2. Получение API credentials

1. Откройте https://my.telegram.org
2. Войдите с номером телефона
3. Перейдите в **API development tools**
4. Создайте приложение (любое название)
5. Скопируйте `api_id` и `api_hash`

### 3. Настройка переменных окружения

```bash
export TELEGRAM_API_ID='ваш_api_id'
export TELEGRAM_API_HASH='ваш_api_hash'
export TELEGRAM_PHONE='+79161234567'
```

**Важно:** После первой авторизации сессия сохраняется в `.gates/telegram_session.session`. Повторная авторизация не требуется.

---

## Использование

### Базовое использование

```python
from telegram_group_gate import TelegramGroupGate
import asyncio

async def main():
    # Инициализация
    gate = TelegramGroupGate()
    
    # Авторизация (один раз)
    await gate.authenticate()
    
    # Информация о группе
    chat_info = await gate.get_chat_info("Париж 2025")
    print(f"Группа: {chat_info['title']}")
    
    # Чтение сообщений
    messages = await gate.read_messages("Париж 2025", limit=100)
    print(f"Прочитано: {len(messages)} сообщений")
    
    # Экспорт Substance
    substance = await gate.export_substance("Париж 2025", messages_limit=500)
    
    # Закрытие
    await gate.close()

asyncio.run(main())
```

### Обработка группы "Париж 2025"

Готовый скрипт для полной обработки группы:

```bash
cd ".gates"
python3 process_paris_2025_group.py
```

Скрипт:
- ✅ Читает всю историю группы
- ✅ Экспортирует в Substance формат
- ✅ Сохраняет в структурированном виде
- ✅ Создает текстовый дамп для чтения

---

## API Reference

### `TelegramGroupGate`

#### `__init__(api_id=None, api_hash=None, phone=None, session_file=None)`

Инициализация Gate.

**Параметры:**
- `api_id`: Telegram API ID (или из `TELEGRAM_API_ID`)
- `api_hash`: Telegram API Hash (или из `TELEGRAM_API_HASH`)
- `phone`: Номер телефона (или из `TELEGRAM_PHONE`)
- `session_file`: Путь к файлу сессии (по умолчанию `.gates/telegram_session.session`)

#### `async authenticate()`

Авторизация в Telegram. Вызывается автоматически при первом использовании.

**Возвращает:**
```python
{
    'authenticated': True,
    'user_id': 123456789,
    'username': 'username',
    'first_name': 'Имя',
    'phone': '+79161234567'
}
```

#### `async get_chat_info(chat_identifier)`

Получить информацию о группе.

**Параметры:**
- `chat_identifier`: Имя группы, username (@groupname) или ID чата

**Возвращает:**
```python
{
    'id': -1001234567890,
    'title': 'Париж 2025',
    'type': 'group',
    'username': 'paris2025',
    'member_count': 25
}
```

#### `async read_messages(chat_identifier, limit=100, offset_date=None, min_id=None)`

Прочитать сообщения из группы.

**Параметры:**
- `chat_identifier`: Имя группы или ID
- `limit`: Максимальное количество сообщений
- `offset_date`: Читать сообщения до этой даты
- `min_id`: Минимальный ID сообщения (для инкрементального чтения)

**Возвращает:**
```python
[
    {
        'message_id': 123,
        'date': '2025-01-15T10:30:00',
        'text': 'Текст сообщения',
        'from_user': {
            'id': 123456789,
            'username': 'username',
            'first_name': 'Имя'
        },
        'media': {
            'type': 'photo',
            'file_id': '...'
        },
        'reply_to': {'message_id': 122},
        'forward_from': {...}
    },
    ...
]
```

#### `async get_group_members(chat_identifier)`

Получить список участников группы.

**Возвращает:**
```python
[
    {
        'id': 123456789,
        'username': 'username',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'is_bot': False
    },
    ...
]
```

#### `async export_substance(chat_identifier, messages_limit=500, include_members=True)`

Экспорт Substance из группы.

**Возвращает:**
```python
{
    'provider': 'telegram_group',
    'timestamp': '2025-01-15T10:30:00Z',
    'chat': {...},
    'messages': [...],
    'members': [...],
    'statistics': {
        'total_messages': 500,
        'total_members': 25,
        'messages_with_media': 50,
        'messages_with_text': 450,
        'date_range': {
            'oldest': '2024-12-01T00:00:00',
            'newest': '2025-01-15T10:30:00'
        }
    }
}
```

---

## Интеграция с архитектурой Gates

### Структура Substance

Telegram Group Gate экспортирует Substance в стандартном формате:

```json
{
  "provider": "telegram_group",
  "timestamp": "ISO 8601",
  "chat": {...},
  "messages": [...],
  "members": [...],
  "statistics": {...}
}
```

### Использование в проектах

```python
from telegram_group_gate import TelegramGroupGate

# В проекте "Ольга"
gate = TelegramGroupGate()
substance = await gate.export_substance("Париж 2025")

# Substance готов для использования в других Gates
```

---

## Примеры

### Чтение последних сообщений

```python
gate = TelegramGroupGate()
await gate.authenticate()

messages = await gate.read_messages("Париж 2025", limit=50)

for msg in messages:
    user = msg.get('from_user', {})
    print(f"{user.get('first_name')}: {msg.get('text')}")
```

### Экспорт и сохранение

```python
import json

gate = TelegramGroupGate()
substance = await gate.export_substance("Париж 2025", messages_limit=1000)

with open('paris2025_substance.json', 'w', encoding='utf-8') as f:
    json.dump(substance, f, ensure_ascii=False, indent=2)
```

### Инкрементальное чтение

```python
# Первое чтение
messages1 = await gate.read_messages("Париж 2025", limit=100)
last_id = messages1[-1]['message_id'] if messages1 else None

# Второе чтение (только новые)
if last_id:
    messages2 = await gate.read_messages("Париж 2025", limit=100, min_id=last_id)
```

---

## Обработка группы "Париж 2025"

Готовый скрипт `process_paris_2025_group.py` выполняет полную обработку:

1. **Чтение истории** — до 1000 сообщений
2. **Экспорт Substance** — стандартный формат
3. **Сохранение результатов:**
   - `substance_telegram_paris2025_*.json` — полный Substance
   - `messages_*.json` — только сообщения
   - `members_*.json` — список участников
   - `dump_*.txt` — текстовый дамп для чтения
   - `statistics_*.json` — статистика экспорта

**Запуск:**

```bash
cd ".gates"
python3 process_paris_2025_group.py
```

---

## Troubleshooting

### Ошибка: "Чат не найден"

**Причины:**
- Неверное имя группы
- Вы не являетесь участником группы
- Группа приватная и требует точного username

**Решение:**
- Используйте точное имя группы или username (@groupname)
- Убедитесь, что вы участник группы

### Ошибка: "Требуется авторизация"

**Причины:**
- Первый запуск
- Сессия истекла

**Решение:**
- Запустите скрипт, введите код из SMS
- Сессия сохранится автоматически

### Ошибка: "Не удалось получить участников"

**Причины:**
- Группа не позволяет получать список участников
- Недостаточно прав

**Решение:**
- Это нормально для некоторых групп
- Скрипт продолжит работу без списка участников

---

## Безопасность

- ✅ Сессия хранится локально в `.gates/telegram_session.session`
- ✅ API credentials в переменных окружения (не в коде)
- ✅ Сессия не передается третьим лицам

**Рекомендации:**
- Добавьте `.gates/telegram_session.session` в `.gitignore`
- Не коммитьте API credentials в репозиторий

---

## Интеграция с другими Gates

Telegram Group Gate интегрируется с:

- **Google Gate** — экспорт в Google Sheets
- **Archive Gate** — сохранение в архив
- **Webhooks** — real-time обновления (в разработке)

---

**Последнее обновление:** 2025-01-15

