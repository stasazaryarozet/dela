# Ссылки на актуальную документацию Meta

**Дата обновления:** 18 ноября 2025

---

## Facebook Login Permissions

**Источник:** https://developers.facebook.com/docs/permissions/reference

### Валидные базовые permissions:
- `public_profile` - базовая информация профиля
- `email` - email адрес

### Валидные Pages permissions:
- `pages_show_list` - список страниц пользователя
- `pages_read_engagement` - чтение метрик страниц
- `pages_manage_posts` - управление постами
- `pages_read_user_content` - чтение контента пользователей

### Business Management:
- `business_management` - управление бизнес-аккаунтами Meta

---

## Instagram Graph API

**Источник:** https://developers.facebook.com/docs/instagram-api

**Важно:** Instagram permissions НЕ запрашиваются напрямую через Facebook Login.
Доступ к Instagram получается через связанные Facebook Pages.

**Процесс:**
1. Получить Page Access Token через `pages_show_list`
2. Запросить `instagram_business_account` для Page
3. Использовать Instagram Account ID для работы с Instagram API

---

## WhatsApp Business API

**Источник:** https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

**Важно:** WhatsApp Business API требует:
1. Meta App с добавленным WhatsApp Product
2. WhatsApp Business Account (WABA)
3. Phone Number подключенный к WABA
4. System User Token или Page Access Token (не User Access Token)

**Доступ через API:**
- Через Business Management API: `/me/businesses/{business-id}/owned_whatsapp_business_accounts`
- Через Meta App: `/{app-id}/whatsapp_business_accounts` (требует System User Token)

**Для отправки сообщений:**
- Требуется Phone Number ID (не номер телефона)
- Требуется Access Token с правами `whatsapp_business_messaging` (через System User)

---

## Long-lived Tokens

**Источник:** https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived-tokens-and-pages-tokens

**Процесс:**
1. Получить short-lived token через OAuth
2. Обменять на long-lived token (60 дней) через `/oauth/access_token` с `grant_type=fb_exchange_token`
3. Для Pages: получить Page Access Token (не истекает, если Page не удалена)

---

## Текущая реализация

Скрипт `deep_integration_auth.py` использует:
- ✅ Валидные Facebook Login permissions
- ✅ Обмен на long-lived token (60 дней)
- ✅ Получение Instagram через Pages
- ✅ Попытка получения WhatsApp через Business Management API

**Ограничения:**
- WhatsApp требует System User Token для полного доступа
- System User Token создается в Meta App Dashboard, не через OAuth


