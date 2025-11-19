# Быстрый старт — Глубокая интеграция с Meta

## Шаг 1: Получить App Secret

1. Откройте: https://developers.facebook.com/apps/848486860991509/settings/basic/
2. Найдите "App Secret"
3. Нажмите "Show"
4. Скопируйте секрет

## Шаг 2: Сохранить App Secret

Создайте файл `.gates/meta/.env`:
```
META_APP_SECRET=ваш_секрет_здесь
```

## Шаг 3: Запустить авторизацию

```bash
python3 .gates/meta/deep_integration_auth.py
```

## Что произойдет:

1. ✅ Скрипт проверит App Secret
2. ✅ Откроет браузер с формой авторизации Meta
3. ✅ Вы войдете от аккаунта Ольги и разрешите права
4. ✅ Токен будет сохранен автоматически в `.gates/meta/credentials.json`
5. ✅ Скрипт завершится автоматически

## После авторизации:

- ✅ Токен действителен 60 дней
- ✅ Доступ к Instagram через связанные Pages
- ✅ Доступ к WhatsApp Business (если настроен)
- ✅ Доступ к Facebook Pages

## Использование токена:

```python
from .gates.meta.meta_gate import MetaGate

gate = MetaGate()
# Теперь можно использовать для Instagram, WhatsApp и т.д.
```


