# Настройка Meta Gate (Instagram)

## Требования

- Аккаунт Instagram должен быть **Business** или **Creator** (не Personal)
- Связанная Facebook Page

---

## Шаг 1: Создать приложение в Meta for Developers

1. Перейти на https://developers.facebook.com/apps/create/
2. Выбрать тип: **Business**
3. Указать имя приложения: **"Дела - Ольга"**
4. Нажать **Create App**

---

## Шаг 2: Добавить Instagram Basic Display или Instagram Graph API

1. В Dashboard приложения → **Add Product**
2. Выбрать **Instagram Graph API** (не Basic Display)
3. Нажать **Set Up**

---

## Шаг 3: Получить Access Token

### Через Graph API Explorer (простой способ):

1. Перейти на https://developers.facebook.com/tools/explorer/
2. Выбрать созданное приложение в dropdown
3. В **Permissions** добавить:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_show_list`
4. Нажать **Generate Access Token**
5. Авторизовать приложение
6. Скопировать токен

---

## Шаг 4: Получить Instagram Business Account ID

1. В Graph API Explorer выполнить запрос:

```
GET /me/accounts
```

2. Найти `id` вашей Facebook Page
3. Выполнить запрос (заменив `PAGE_ID`):

```
GET /PAGE_ID?fields=instagram_business_account
```

4. Скопировать `instagram_business_account.id`

---

## Шаг 5: Создать credentials.json

Создать файл `.gates/meta/credentials.json`:

```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "instagram_account_id": "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID"
}
```

---

## Шаг 6: Тест

```bash
cd /Users/azaryarozet/Library/Mobile\ Documents/com~apple~CloudDocs/Дела
python3 .gates/meta_gate.py
```

Должно вывести:
```
✓ Авторизован: Olga Rozet (ID: ...)
✓ Получено постов: 5
```

---

## Важно: Long-Lived Token

По умолчанию токен живет **1 час**.

Для продления до **60 дней**:

1. Получить `App ID` и `App Secret` из Dashboard → Settings → Basic
2. Выполнить запрос (замените параметры):

```
GET https://graph.facebook.com/v18.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id=YOUR_APP_ID&
  client_secret=YOUR_APP_SECRET&
  fb_exchange_token=YOUR_SHORT_LIVED_TOKEN
```

3. Заменить токен в `credentials.json` на полученный

---

## Webhooks (опционально, для real-time)

1. В Dashboard → Webhooks → Instagram
2. Callback URL: `https://your-cloudflare-url.trycloudflare.com/webhook/meta`
3. Verify Token: любая строка (сохраните её)
4. Subscribe to: `feed`, `comments`, `mentions`
