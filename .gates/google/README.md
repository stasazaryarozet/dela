# Google API Integration — Ольга

Максимальный доступ к Gmail + Calendar для системы "Дела".

---

## Архитектура

### **7-дневный цикл (Test Mode):**
- Google OAuth в тестовом режиме аннулирует Refresh Token через 7 дней
- Скрипт автоматически обнаруживает истечение
- Запрашивает повторную авторизацию (HHE: 10 минут каждую неделю)

### **Scope (максимальные):**
```
https://www.googleapis.com/auth/gmail.modify  # Полный доступ к Gmail
https://www.googleapis.com/auth/calendar      # Полный доступ к Calendar
```

**Обоснование:** Максимальный доступ для Sonnet ко всем ресурсам Ольги (не для конкретной задачи, а для системы в целом).

---

## Использование

### **1. Первая настройка (один раз):**

1. Получить `credentials.json` из Google Cloud Console
2. Поместить в `.google/credentials.json`
3. Запустить:

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/Дела/Ольга/.google"
python3 google_gate.py
```

4. Откроется браузер → авторизоваться как Ольга
5. Token сохранится в `token.pickle`

---

### **2. Еженедельная реавторизация (каждые 7 дней):**

**Когда токен истечёт (через 7 дней):**
1. Скрипт автоматически обнаружит
2. Удалит `token.pickle`
3. Запросит повторную авторизацию (браузер откроется)

**HHE:** 10 минут раз в неделю.

---

### **3. Использование в других скриптах:**

```python
from google_gate import GoogleGate

helper = GoogleGate(
    credentials_path='.google/credentials.json',
    token_path='.google/token.pickle'
)

# Gmail
gmail = helper.get_gmail_service()
# ... работа с Gmail API

# Calendar  
calendar = helper.get_calendar_service()
# ... работа с Calendar API
```

---

## Безопасность

### **Файлы (НЕ коммитить в Git):**
- `credentials.json` — секрет Google Cloud
- `token.pickle` — access/refresh tokens

**Добавлено в `.gitignore`:**
```
Ольга/.google/credentials.json
Ольга/.google/token.pickle
```

---

## Альтернативы 7-дневному циклу

### **Вариант А: Публикация приложения**
- Пройти Google OAuth verification
- Получить бессрочный refresh token
- **Trade-off:** HHE-Setup (политика конфиденциальности, проверка Google)

### **Вариант Б: Service Account**
- Использовать Service Account (без OAuth)
- **Trade-off:** Требует Google Workspace (платный)

### **Вариант В: Принять 7-дневный цикл**
- HHE: 10 минут каждую неделю
- **Trade-off:** Приемлемо для частной системы

**Текущее решение:** Вариант В (принят).

---

## История

- **07.11.2025** — Создана интеграция
- **Scope:** `gmail.modify` + `calendar` (максимальные)
- **Режим:** Test Mode (7-дневный refresh token)

---

**Максимальный доступ. Глубокая интеграция. MHE-архитектура.**
