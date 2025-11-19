# Gates Architecture

## Принцип

**Gate** — универсальный интерфейс для подключения внешнего провайдера к "Делам".

Каждый Gate обеспечивает:
- **Auth** — авторизация (OAuth / API Key / Token)
- **Read** — чтение данных
- **Write** — запись данных
- **Webhooks** — регистрация real-time событий
- **Export** — формат данных для Substance

---

## Структура Gate

```python
class ProviderGate:
    def __init__(self, credentials_path=None):
        """Инициализация с путем к credentials"""
        
    def authenticate(self):
        """Авторизация в провайдере"""
        
    def read(self, resource_type, filters=None):
        """Чтение данных (посты, сообщения, события)"""
        
    def write(self, resource_type, data):
        """Запись данных (публикация, ответ)"""
        
    def setup_webhook(self, callback_url, events):
        """Регистрация webhook для событий"""
        
    def export_substance(self):
        """Экспорт всех данных в формате для Substance"""
        return {
            'provider': 'provider_name',
            'timestamp': 'ISO 8601',
            'data': {...}
        }
```

---

## Доступные Gates

- **`google/`** (google_gate.py) — Gmail, Calendar, Drive, Contacts, Sheets, Docs, Forms ✅
- **`meta_gate.py`** — Instagram, Facebook (требует настройки)
- **`telegram_remote_gate.py`** — Публикация через удаленный Telegram-бот ✅
- **`telegram_archive_gate.py`** — Доступ к архиву бота (Яндекс.Диск, требует YANDEX_DISK_TOKEN)
- **`telegram_group_gate.py`** — Чтение истории группы через Telethon (User API) ✅
- **`whatsapp/`** (whatsapp_multi_user_gate.py) — WhatsApp Business API для Azarya и Olga ✅
- **`calcom_gate.py`** — Cal.com API (в разработке)

---

## Telegram-бот (интеграция)

**Существующий бот:** `telegram-bot/` (работает на Railway.app)

**Функции бота:**
- Архивация контента из чатов (видео, аудио, текст, фото, документы)
- Хранение на Яндекс.Диске (зашифровано)
- Глобальная дедупликация файлов

**Gates для бота:**

1. **`telegram_remote_gate.py`** — Публикация сообщений:
   - Требует: `TELEGRAM_BOT_TOKEN`
   - Возможности: Отправка текста, фото, видео, документов
   - Тест: `python3 .gates/telegram_remote_gate.py`

2. **`telegram_archive_gate.py`** — Доступ к архиву:
   - Требует: `TELEGRAM_BOT_TOKEN` + `YANDEX_DISK_TOKEN`
   - Возможности: Чтение контента из архива, метаданные, статистика
   - Тест: `python3 .gates/telegram_archive_gate.py`

3. **`telegram_group_gate.py`** — Чтение истории группы:
   - Требует: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`
   - Возможности: Полная история группы, участники, экспорт Substance
   - Тест: `python3 .gates/telegram_group_gate.py "Название группы"`
   - Документация: `TELEGRAM_GROUP_GATE.md`

---

## Использование в проектах

Проект определяет, какие Gates активны через `.project_config.json`:

```json
{
  "project": "Ольга",
  "gates": {
    "google": {
      "enabled": true,
      "scopes": ["gmail", "calendar"]
    },
    "meta": {
      "enabled": true,
      "accounts": ["@olga.rozet"]
    },
    "telegram": {
      "enabled": true,
      "channels": ["@olgarozet_channel"]
    },
    "calcom": {
      "enabled": true,
      "username": "olgarozet"
    }
  }
}
```

---

## ZHE Webhooks

Все Gates регистрируют webhooks в централизованном сервере (`.webhooks/webhook_server.py`).

При любом событии → автоматический экспорт Substance → система реагирует (< 1 сек).
