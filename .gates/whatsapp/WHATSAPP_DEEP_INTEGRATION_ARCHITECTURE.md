# WhatsApp Deep Integration Architecture

**Дата:** 17 ноября 2025  
**Статус:** Архитектурная спецификация  
**Для:** Azarya и Olga

---

## 🎯 Принципы интеграции

### Глубоко
- Полный доступ ко всем возможностям WhatsApp Business API
- Чтение и отправка сообщений, медиа, статусов
- Управление контактами и группами
- Webhooks для real-time событий
- Интеграция с Substance Export

### Доверительно
- Изолированные credentials для каждого пользователя
- Шифрование токенов и чувствительных данных
- Аудит всех операций
- Принцип минимальных прав доступа

### Вечно
- Автоматическое обновление токенов
- Резервное копирование данных
- Версионирование конфигураций
- Долгосрочная совместимость с API

---

## 📐 Архитектура

```
.gates/whatsapp/
├── README.md                          # Документация
├── WHATSAPP_DEEP_INTEGRATION_ARCHITECTURE.md  # Этот файл
│
├── credentials/                       # Изолированные credentials
│   ├── azarya_credentials.json       # Credentials Azarya
│   ├── olga_credentials.json         # Credentials Olga
│   └── .gitignore                    # Исключить из Git
│
├── sessions/                          # Сессии и токены
│   ├── azarya_token.pickle           # Токен Azarya (автообновление)
│   ├── olga_token.pickle             # Токен Olga (автообновление)
│   └── .gitignore                    # Исключить из Git
│
├── whatsapp_gate.py                  # Базовый Gate (улучшенный)
├── whatsapp_multi_user_gate.py      # Multi-user Gate для Azarya и Olga
├── whatsapp_webhook_server.py        # Webhook сервер
├── whatsapp_substance_export.py      # Substance Export
│
└── scripts/                           # Утилиты
    ├── setup_azarya_whatsapp.py      # Настройка для Azarya
    ├── setup_olga_whatsapp.py        # Настройка для Olga
    ├── test_connection.py            # Тест подключения
    └── export_messages.py            # Экспорт сообщений
```

---

## 🔐 Модель безопасности

### Изоляция credentials

**Принцип:** Каждый пользователь имеет изолированные credentials и сессии.

```json
// credentials/azarya_credentials.json
{
  "user": "azarya",
  "access_token": "EAA...",
  "phone_number_id": "123456789",
  "business_account_id": "987654321",
  "webhook_verify_token": "unique_token_azarya",
  "encrypted": false
}

// credentials/olga_credentials.json
{
  "user": "olga",
  "access_token": "EAA...",
  "phone_number_id": "111222333",
  "business_account_id": "444555666",
  "webhook_verify_token": "unique_token_olga",
  "encrypted": false
}
```

### Автоматическое обновление токенов

**Принцип:** Токены обновляются автоматически при истечении (7 дней для WhatsApp).

```python
class WhatsAppGate:
    def __init__(self, user='azarya'):
        self.user = user
        self.credentials_path = f'.gates/whatsapp/credentials/{user}_credentials.json'
        self.token_path = f'.gates/whatsapp/sessions/{user}_token.pickle'
        
    def refresh_token_if_needed(self):
        """Автоматическое обновление токена при истечении"""
        # Проверка срока действия
        # Обновление через refresh_token
        # Сохранение нового токена
```

---

## 🔄 Интеграция с архитектурой проекта

### Уровень 1: Root Level (○)

**WhatsApp Gate** доступен всем проектам:

```python
from .gates.whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate

# Для Azarya
gate_azarya = WhatsAppMultiUserGate(user='azarya')
messages = gate_azarya.get_messages(limit=50)

# Для Olga
gate_olga = WhatsAppMultiUserGate(user='olga')
gate_olga.send_message(to='79991234567', message='Привет!')
```

### Уровень 2: Project Level

**Проекты используют WhatsApp Gate по необходимости:**

```python
# olga/design-travels/PARIS-2026/whatsapp_integration.py
from ...gates.whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate

gate = WhatsAppMultiUserGate(user='olga')
# Отправка уведомлений участникам тура
```

### Уровень 3: Webhooks

**Централизованный webhook сервер:**

```
.webhooks/webhook_server.py
  ├── /webhook/whatsapp/azarya    # Webhook для Azarya
  └── /webhook/whatsapp/olga      # Webhook для Olga
```

---

## 📡 Webhook Architecture

### Структура webhook

```python
# .webhooks/whatsapp_webhook_handler.py

class WhatsAppWebhookHandler:
    """Обработчик webhook для WhatsApp"""
    
    def handle_message(self, user, payload):
        """Обработка входящего сообщения"""
        # Определение пользователя (azarya/olga)
        # Парсинг payload
        # Сохранение в Substance
        # Триггер действий (если нужно)
    
    def handle_status(self, user, payload):
        """Обработка статуса сообщения"""
        # Обновление статуса отправленного сообщения
```

### События

- `messages` — входящие сообщения
- `message_status` — статусы отправленных сообщений
- `message_template_status` — статусы шаблонов
- `phone_number_name_update` — обновление имени номера

---

## 💾 Substance Export

### Формат экспорта

```json
{
  "provider": "whatsapp_business",
  "user": "azarya",
  "timestamp": "2025-11-17T...",
  "data": {
    "account": {
      "business_account_id": "...",
      "phone_number_id": "...",
      "name": "..."
    },
    "messages": [
      {
        "id": "...",
        "from": "79991234567",
        "to": "79997654321",
        "text": "...",
        "timestamp": "...",
        "status": "delivered"
      }
    ],
    "contacts": [...],
    "media": [...]
  }
}
```

---

## 🛠️ Реализация

### Этап 1: Multi-user Gate

**Файл:** `.gates/whatsapp/whatsapp_multi_user_gate.py`

**Возможности:**
- Поддержка нескольких пользователей (azarya, olga)
- Изолированные credentials и сессии
- Автоматическое обновление токенов
- Единый интерфейс для всех операций

### Этап 2: Webhook Server

**Файл:** `.webhooks/whatsapp_webhook_handler.py`

**Возможности:**
- Обработка webhook для каждого пользователя
- Парсинг событий WhatsApp
- Интеграция с Substance Export
- Триггеры автоматических действий

### Этап 3: Интеграция в проекты

**Интеграция в:**
- `olga/design-travels/PARIS-2026/` — уведомления участникам
- `olga/consultations/` — напоминания о консультациях
- `azarya/` — общие коммуникации

---

## 📋 Чеклист внедрения

### Для Azarya
- [ ] Создать Meta App для WhatsApp Business
- [ ] Настроить WhatsApp Business Account
- [ ] Получить credentials (access_token, phone_number_id)
- [ ] Сохранить в `.gates/whatsapp/credentials/azarya_credentials.json`
- [ ] Протестировать подключение

### Для Olga
- [ ] Создать Meta App для WhatsApp Business (или использовать общий)
- [ ] Настроить WhatsApp Business Account
- [ ] Получить credentials
- [ ] Сохранить в `.gates/whatsapp/credentials/olga_credentials.json`
- [ ] Протестировать подключение

### Общее
- [ ] Настроить webhook сервер
- [ ] Зарегистрировать webhook в Meta App Dashboard
- [ ] Протестировать получение сообщений
- [ ] Интегрировать с Substance Export
- [ ] Документировать использование

---

## 🔗 Ссылки

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Meta App Dashboard](https://developers.facebook.com/apps/)
- [Webhook Setup Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)

---

## 📝 Примечания

**Безопасность:**
- Credentials хранятся локально, не коммитятся в Git
- Токены автоматически обновляются
- Webhook verify_token уникален для каждого пользователя

**Масштабируемость:**
- Легко добавить новых пользователей
- Каждый пользователь изолирован
- Общий код в базовом Gate

**Совместимость:**
- Следует паттерну Gates Architecture
- Интегрируется с Substance Export
- Совместим с webhook сервером проекта


