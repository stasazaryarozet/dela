# Быстрый старт: Обработка группы "Париж 2025"

**Время:** 5 минут  
**Результат:** Полный экспорт содержания группы в Substance формат

---

## Шаг 1: Проверка зависимостей

```bash
pip install telethon
```

---

## Шаг 2: Настройка переменных окружения

Если у вас уже есть Telegram API credentials (из `telegram-bot/tools/telegram_auth_once.sh`):

```bash
export TELEGRAM_API_ID='28482390'
export TELEGRAM_API_HASH='7392719c7cef090ff844c1da3f05f807'
export TELEGRAM_PHONE='+79854417201'
```

**Или получите новые:**
1. Откройте https://my.telegram.org
2. Войдите с номером телефона
3. Перейдите в **API development tools**
4. Создайте приложение
5. Скопируйте `api_id` и `api_hash`

---

## Шаг 3: Первая авторизация (один раз)

Запустите Gate для авторизации:

```bash
cd ".gates"
python3 telegram_group_gate.py "Париж 2025"
```

**При первом запуске:**
- Telegram пришлет SMS с кодом
- Введите код в терминал
- Сессия сохранится в `.gates/telegram_session.session`
- Повторная авторизация не потребуется

---

## Шаг 4: Обработка группы

Запустите скрипт обработки:

```bash
cd ".gates"
python3 process_paris_2025_group.py
```

**Скрипт выполнит:**
- ✅ Чтение истории группы (до 1000 сообщений)
- ✅ Экспорт в Substance формат
- ✅ Сохранение результатов в структурированном виде

---

## Результаты

Результаты сохраняются в:

```
Ольга/Дизайн-путешествия/PARIS-2026/telegram_group/
├── messages_YYYYMMDD_HHMMSS.json    # Все сообщения
├── members_YYYYMMDD_HHMMSS.json     # Участники группы
├── dump_YYYYMMDD_HHMMSS.txt         # Текстовый дамп
└── statistics_YYYYMMDD_HHMMSS.json  # Статистика

.substance/
└── substance_telegram_paris2025_YYYYMMDD_HHMMSS.json  # Полный Substance
```

---

## Использование результатов

### Чтение текстового дампа

```bash
cat "Ольга/Дизайн-путешествия/PARIS-2026/telegram_group/dump_*.txt"
```

### Анализ Substance в Python

```python
import json

with open('.substance/substance_telegram_paris2025_*.json', 'r') as f:
    substance = json.load(f)

print(f"Сообщений: {substance['statistics']['total_messages']}")
print(f"Участников: {substance['statistics']['total_members']}")

for msg in substance['messages'][:10]:
    print(f"{msg['from_user']['first_name']}: {msg['text']}")
```

### Интеграция с Google Sheets

```python
from .gates.google.google_gate import GoogleGate
import json

# Загрузить Substance
with open('.substance/substance_telegram_paris2025_*.json', 'r') as f:
    substance = json.load(f)

# Экспорт в Google Sheets
gate = GoogleGate()
sheets = gate.sheets()

# Создать таблицу с сообщениями
# ...
```

---

## Troubleshooting

### Ошибка: "Группа не найдена"

**Решение:**
- Убедитесь, что вы участник группы "Париж 2025"
- Попробуйте точное имя группы или username (@groupname)
- Проверьте, что группа существует и доступна

### Ошибка: "Требуется авторизация"

**Решение:**
- Запустите `telegram_group_gate.py` для авторизации
- Введите код из SMS
- Сессия сохранится автоматически

### Ошибка: "Не удалось получить участников"

**Это нормально:**
- Некоторые группы не позволяют получать список участников
- Скрипт продолжит работу без списка участников
- Сообщения будут экспортированы

---

## Повторный запуск

После первой авторизации просто запускайте:

```bash
python3 process_paris_2025_group.py
```

Сессия сохраняется, повторная авторизация не требуется.

---

**Готово!** Группа "Париж 2025" обработана и экспортирована в Substance формат.

