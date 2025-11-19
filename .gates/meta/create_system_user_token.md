# Создание System User Token для глубокой интеграции с Meta

**Цель:** Максимально глубокая и вечная интеграция со всеми платформами Meta  
**Проблема:** User Access Token не имеет прав на WhatsApp API и другие бизнес-функции  
**Решение:** Создать System User Token с полными правами через Business Settings

---

## 🔧 Шаги создания System User Token

### Шаг 1: Открыть Business Settings

1. Откройте **Meta Business Settings**:
   - https://business.facebook.com/settings
   - Войдите под аккаунтом Ольги Розет

2. Убедитесь, что вы находитесь в правильном бизнес-аккаунте:
   - **Ольга Розет** (ID: 172493590254831)

---

### Шаг 2: Создать System User

1. В левом меню выберите **"System Users"**
2. Нажмите **"Add"** → **"Create New System User"**
3. Заполните:
   - **Name:** `Meta Deep Integration` (или `Meta Full Platform Integration`)
   - **System User Role:** `Admin` (для максимального доступа)
   - **Financial Role:** `Admin` (опционально, только если планируете управлять рекламой/платежами)
4. Нажмите **"Create System User"**

**Примечание о финансовой роли:**
- **Не требуется** для API интеграции (WhatsApp, Pages, Instagram)
- **Нужна** только если планируете:
  - Управлять рекламой через API
  - Совершать финансовые транзакции
  - Получать доступ к биллингу и платежам
- Для глубокой интеграции с контентом и сообщениями достаточно роли `Admin` без финансовой роли

---

### Шаг 3: Назначить права на все активы

1. Найдите созданного System User в списке
2. Нажмите **"Assign Assets"**
3. Назначьте права на **все активы**:

   **Facebook Pages:**
   - ✅ Выберите все страницы (Home-resurs, Творческая Мастерская "Ольги Розет")
   - ✅ Права: **Full Control**

   **Instagram Accounts:**
   - ✅ Выберите все связанные Instagram аккаунты
   - ✅ Права: **Full Control**

   **WhatsApp Accounts:**
   - ✅ Выберите все WhatsApp Business Accounts
   - ✅ Права: **Full Control**

   **Business Assets:**
   - ✅ Выберите бизнес-аккаунт "Ольга Розет"
   - ✅ Права: **Full Control**

4. Нажмите **"Save Changes"**

---

### Шаг 4: Сгенерировать System User Token

1. Вернитесь к списку System Users
2. Найдите созданного System User
3. Нажмите **"Generate New Token"**
4. Выберите приложение:
   - Ваше приложение (ID: 848486860991509)
5. Выберите права (scopes) — **максимально полный набор**:
   
   **WhatsApp:**
   - ✅ `whatsapp_business_management`
   - ✅ `whatsapp_business_messaging`
   - ✅ `whatsapp_business_analytics`
   
   **Facebook Pages:**
   - ✅ `pages_show_list`
   - ✅ `pages_read_engagement`
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_user_content`
   - ✅ `pages_manage_metadata`
   - ✅ `pages_manage_ads`
   
   **Instagram:**
   - ✅ `instagram_basic`
   - ✅ `instagram_manage_comments`
   - ✅ `instagram_manage_insights`
   - ✅ `instagram_content_publish`
   
   **Business Management:**
   - ✅ `business_management`
   - ✅ `ads_management`
   - ✅ `ads_read`
   
   **Дополнительные:**
   - ✅ `public_profile`
   - ✅ `email` (если доступно)

6. Нажмите **"Generate Token"**
7. **Скопируйте токен** (он показывается только один раз!)

---

### Шаг 5: Сохранить токен

Сохраните System User Token в `.gates/meta/.env`:

```bash
META_SYSTEM_USER_TOKEN=your_system_user_token_here
```

Или запустите скрипт для автоматического сохранения:

```bash
python3 .gates/meta/save_system_user_token.py
```

---

## ✅ После создания System User Token

1. Сохраните токен:
   ```bash
   python3 .gates/meta/save_system_user_token.py
   ```

2. Обновите credentials для всех платформ:
   ```bash
   # WhatsApp
   python3 .gates/whatsapp/setup_whatsapp_cloud_api.py
   
   # Facebook Pages
   python3 .gates/meta/refresh_credentials.py
   
   # Instagram
   python3 .gates/meta/refresh_credentials.py
   ```

3. Проверьте доступ ко всем платформам:
   ```bash
   # WhatsApp
   python3 .gates/whatsapp/access_via_meta_credentials.py
   
   # Все платформы
   python3 .gates/meta/test_full_access.py
   ```

4. Теперь должны быть доступны:
   - ✅ WhatsApp Business Accounts и Phone Numbers
   - ✅ Facebook Pages (публикация, управление)
   - ✅ Instagram Accounts (публикация, аналитика)
   - ✅ Business Management API
   - ✅ Отправка и получение сообщений WhatsApp
   - ✅ Управление постами и контентом

---

## 📚 Альтернативные способы

### Вариант A: Через Meta App Dashboard

1. Откройте: https://developers.facebook.com/apps/848486860991509/
2. Перейдите в **"WhatsApp"** → **"API Setup"**
3. Используйте **"Temporary Access Token"** для тестирования
4. Для production создайте System User Token

### Вариант B: Через Graph API Explorer

1. Откройте: https://developers.facebook.com/tools/explorer/
2. Выберите ваше приложение
3. Используйте **"Get Token"** → **"System User Token"**
4. Скопируйте токен

---

## ⚠️ Важные замечания

1. **System User Token** не истекает автоматически (в отличие от User Token)
2. Токен можно **отозвать** в любой момент в Business Settings
3. Для **production** рекомендуется использовать System User Token
4. **Temporary Access Token** из Dashboard действителен только 24 часа

---

## 🔍 Проверка прав

После создания System User Token проверьте доступ:

```bash
curl -X GET "https://graph.facebook.com/v18.0/me/businesses?access_token=YOUR_SYSTEM_USER_TOKEN"
```

Должен вернуться список бизнес-аккаунтов с WhatsApp Business Accounts.

