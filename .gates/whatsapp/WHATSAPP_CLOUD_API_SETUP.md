# Настройка WhatsApp Cloud API

**Документация:** https://developers.facebook.com/docs/whatsapp/  
**Дата:** 18 ноября 2025

---

## 📋 Обзор

WhatsApp Business Platform состоит из двух основных API:

1. **Cloud API** — для отправки и получения сообщений (обязателен)
2. **Business Management API** — для управления аккаунтом и шаблонами

---

## ✅ Требования

1. ✅ Meta App создан и настроен
2. ✅ OAuth авторизация завершена (долгоживущий токен получен)
3. ⚠️ WhatsApp продукт добавлен в Meta App Dashboard
4. ⚠️ WhatsApp Business Account настроен
5. ⚠️ Номер телефона подключен

---

## 🔧 Шаги настройки

### Шаг 1: Добавить продукт WhatsApp

1. Откройте Meta App Dashboard:
   - https://developers.facebook.com/apps/848486860991509/
   - Войдите под аккаунтом Ольги Розет

2. В разделе **"Products"** найдите **"WhatsApp"**
   - Если продукт не добавлен, нажмите **"Add Product"** → **"WhatsApp"**

3. Следуйте инструкциям настройки

---

### Шаг 2: Настроить WhatsApp Business Account

1. В разделе **"WhatsApp"** → **"API Setup"**
2. Выберите или создайте **WhatsApp Business Account**
3. Подключите **номер телефона**
   - Можно использовать существующий номер или получить новый
   - Номер должен быть верифицирован

4. Запишите:
   - **WhatsApp Business Account ID** (WABA ID)
   - **Phone Number ID**
   - **Display Phone Number**

---

### Шаг 3: Получить Access Token

Для Cloud API требуется один из токенов:

#### Вариант A: Page Access Token (проще)
- Используется токен от связанной Facebook Page
- Уже получен через OAuth авторизацию
- Доступен в `.gates/meta/credentials.json`

#### Вариант B: System User Token (рекомендуется)
1. Откройте **Meta Business Settings**
   - https://business.facebook.com/settings
2. Перейдите в **"System Users"**
3. Создайте нового System User
4. Назначьте права:
   - `whatsapp_business_management`
   - `whatsapp_business_messaging`
5. Сгенерируйте **System User Token**
6. Сохраните токен в credentials

---

### Шаг 4: Настроить Webhook (опционально)

Для получения сообщений в реальном времени:

1. В Meta App Dashboard → **WhatsApp** → **Configuration**
2. Настройте **Webhook URL**
3. Укажите **Verify Token**
4. Подпишитесь на события:
   - `messages` — входящие сообщения
   - `message_status` — статусы отправки

---

## 🚀 Использование

После настройки запустите:

```bash
# Автоматическая настройка через API
python3 .gates/whatsapp/setup_whatsapp_cloud_api.py

# Чтение сообщений
python3 .gates/whatsapp/read_olga_messages.py

# Отправка сообщения
python3 .gates/whatsapp/send_message.py
```

---

## 📚 Документация

- **Cloud API:** https://developers.facebook.com/docs/whatsapp/cloud-api
- **Business Management API:** https://developers.facebook.com/docs/whatsapp/business-management-api
- **Phone Numbers:** https://developers.facebook.com/docs/whatsapp/phone-number
- **Webhooks:** https://developers.facebook.com/docs/whatsapp/webhooks
- **Get Started:** https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

---

## ⚠️ Важные замечания

1. **Cloud API обязателен** для отправки/получения сообщений
2. **On-Premises API** устарел (sunset с 23 октября 2025)
3. **Phone Number** требуется для работы
4. **System User Token** рекомендуется для production
5. **Webhook** необходим для получения сообщений в реальном времени

---

## 🔍 Проверка настройки

После настройки проверьте:

```bash
python3 .gates/whatsapp/access_via_meta_credentials.py
```

Должны быть видны:
- ✅ WhatsApp Business Account ID
- ✅ Phone Number ID
- ✅ Access Token

---

## 📝 Текущий статус

- ✅ Meta OAuth авторизация завершена
- ✅ Долгоживущий токен получен (59 дней)
- ✅ Page Access Tokens доступны
- ⚠️ WhatsApp продукт требует настройки в Dashboard
- ⚠️ WhatsApp Business Account требует создания
- ⚠️ Phone Number требует подключения


