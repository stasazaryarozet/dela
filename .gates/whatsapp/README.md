# WhatsApp Deep Integration

**Глубокая, доверительная и вечная интеграция с WhatsApp Business API для Azarya и Olga**

---

## 🎯 Принципы

- **Глубоко:** Полный доступ ко всем возможностям WhatsApp Business API
- **Доверительно:** Изолированные credentials для каждого пользователя
- **Вечно:** Автоматическое обновление токенов, долгосрочная совместимость

---

## 📐 Архитектура

```
.gates/whatsapp/
├── README.md                                    # Этот файл
├── WHATSAPP_DEEP_INTEGRATION_ARCHITECTURE.md   # Архитектурная спецификация
│
├── credentials/                                 # Изолированные credentials
│   ├── azarya_credentials.json                 # Credentials Azarya
│   ├── olga_credentials.json                   # Credentials Olga
│   └── .gitignore                              # Исключить из Git
│
├── sessions/                                    # Сессии и токены
│   ├── azarya_token.pickle                     # Токен Azarya
│   ├── olga_token.pickle                       # Токен Olga
│   └── .gitignore                              # Исключить из Git
│
├── whatsapp_multi_user_gate.py                 # Multi-user Gate
│
└── scripts/                                     # Утилиты
    ├── setup_azarya_whatsapp.py                # Настройка для Azarya
    ├── setup_olga_whatsapp.py                  # Настройка для Olga
    └── test_connection.py                      # Тест подключения
```

---

## 🚀 Быстрый старт

### 1. Настройка для Azarya

```bash
cd .gates/whatsapp/scripts
python3 setup_azarya_whatsapp.py
```

Следуйте инструкциям для получения credentials из Meta App Dashboard.

### 2. Настройка для Olga

```bash
cd .gates/whatsapp/scripts
python3 setup_olga_whatsapp.py
```

### 3. Использование

```python
from .gates.whatsapp.whatsapp_multi_user_gate import WhatsAppMultiUserGate

# Для Azarya
gate_azarya = WhatsAppMultiUserGate(user='azarya')
result = gate_azarya.send_message(to='79991234567', message='Привет!')

# Для Olga
gate_olga = WhatsAppMultiUserGate(user='olga')
messages = gate_olga.get_messages(limit=50)
```

---

## 📡 Webhooks

Webhook сервер находится в `.webhooks/whatsapp_webhook_handler.py`

**Endpoints:**
- `GET/POST /webhook/whatsapp/azarya` — Webhook для Azarya
- `GET/POST /webhook/whatsapp/olga` — Webhook для Olga

**Настройка в Meta App Dashboard:**
1. App → WhatsApp → Configuration → Webhook
2. Callback URL: `https://your-domain.com/webhook/whatsapp/{user}`
3. Verify Token: Из `{user}_credentials.json`

---

## 💾 Substance Export

```python
gate = WhatsAppMultiUserGate(user='azarya')
substance = gate.export_substance(messages_limit=100)

# Substance содержит:
# - Информацию об аккаунте
# - Последние сообщения
# - Статусы сообщений
```

---

## 🔐 Безопасность

- Credentials хранятся локально, не коммитятся в Git
- Каждый пользователь имеет изолированные credentials
- Webhook verify_token уникален для каждого пользователя
- Токены автоматически обновляются при необходимости

---

## 📚 Документация

- [Архитектурная спецификация](WHATSAPP_DEEP_INTEGRATION_ARCHITECTURE.md)
- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp)
- [Meta App Dashboard](https://developers.facebook.com/apps/)

---

## ✅ Статус

- ✅ Multi-user Gate реализован
- ✅ Скрипты настройки готовы
- ✅ Webhook handler готов
- ⏳ Требуется настройка credentials для Azarya и Olga
- ⏳ Требуется настройка webhook в Meta App Dashboard


