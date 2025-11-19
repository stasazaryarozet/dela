# ЯНДЕКС.ДИСК ИНТЕГРАЦИЯ

**Цель:** Постоянное облачное хранилище для telegram-bot (Railway эфемерен)

**Стоимость:** 0₽ (128 GB бесплатно)

---

## ПОЛУЧЕНИЕ ТОКЕНА

### Шаг 1: Регистрация приложения

1. Перейти: https://oauth.yandex.ru/
2. Нажать "Зарегистрировать новое приложение"
3. Заполнить:
   - **Название:** Telegram Archive Bot
   - **Платформы:** Веб-сервисы
   - **Redirect URI:** https://oauth.yandex.ru/verification_code
   - **Права доступа:**
     - ✅ Яндекс.Диск REST API (cloud_api:disk.write)

4. Сохранить **Client ID** и **Client Secret**

### Шаг 2: Получение OAuth токена

**Вручную (через браузер):**

1. Открыть URL (замените `<CLIENT_ID>`):
```
https://oauth.yandex.ru/authorize?response_type=token&client_id=<CLIENT_ID>
```

2. Авторизоваться в Яндекс
3. Разрешить доступ
4. Скопировать токен из redirect URL:
```
https://oauth.yandex.ru/verification_code#access_token=ВАШТОКЕН&...
```

**Через curl (программно):**

```bash
# 1. Получить код авторизации (открыть в браузере):
https://oauth.yandex.ru/authorize?response_type=code&client_id=<CLIENT_ID>

# 2. Обменять код на токен:
curl -X POST https://oauth.yandex.ru/token \
  -d "grant_type=authorization_code" \
  -d "code=<КОД_ИЗ_БРАУЗЕРА>" \
  -d "client_id=<CLIENT_ID>" \
  -d "client_secret=<CLIENT_SECRET>"
```

Токен из JSON ответа: `access_token`

---

## НАСТРОЙКА RAILWAY

### Добавить переменную окружения:

```bash
cd ~/dela/telegram-bot
railway variables set YANDEX_DISK_TOKEN="<ВАШ_ТОКЕН>"
```

Или через веб-интерфейс:
1. https://railway.app/project/<PROJECT_ID>
2. Service: telegram-bot
3. Variables → New Variable
4. `YANDEX_DISK_TOKEN` = ваш токен

---

## ТЕСТИРОВАНИЕ

### Локально:

```bash
export YANDEX_DISK_TOKEN="ваш_токен"
cd ~/dela/tools
python3 yandex_storage.py test.txt /TelegramArchive/test.txt
```

Должно вывести: `✅ Загружено: /TelegramArchive/test.txt`

### В Railway:

После настройки переменной бот автоматически начнет загружать файлы в облако.

Проверить логи:
```bash
cd ~/dela/telegram-bot
railway logs
```

---

## СТРУКТУРА ХРАНИЛИЩА

```
Яндекс.Диск:/
└── TelegramArchive/
    ├── -1001234567890_N_O_S/
    │   ├── videos/
    │   ├── audio/
    │   ├── voice/
    │   ├── photos/
    │   ├── documents/
    │   ├── text/
    │   ├── metadata/
    │   └── transcripts/
    └── processed_files.json
```

---

## БЕЗОПАСНОСТЬ

**Токен — это ключ к вашему Яндекс.Диску!**

- ✅ Хранить только в переменных окружения (не в коде)
- ✅ Добавить в `.gitignore`
- ✅ Не логировать
- ❌ Не коммитить в Git
- ❌ Не публиковать

**Если токен утек:**
1. https://oauth.yandex.ru/
2. Мои приложения → Telegram Archive Bot → Удалить все токены
3. Создать новый токен

---

## API ЛИМИТЫ

**Яндекс.Диск WebDAV:**
- Размер файла: до 50 GB
- Скорость: без ограничений
- Квота: 128 GB бесплатно

**Рекомендация:** Если архив > 100 GB, настроить автоудаление старых файлов или перейти на платный тариф (10₽/мес за 100 GB).

---

## ОТЛАДКА

**Проблема: "401 Unauthorized"**
→ Токен неверен или истек. Получить новый.

**Проблема: "507 Insufficient Storage"**
→ Диск заполнен. Очистить место или увеличить квоту.

**Проблема: "409 Conflict"**
→ Родительская директория не существует (создается автоматически).

---

**Статус:** Готово к настройке  
**Зависимости:** `requests` (уже в requirements.txt)

