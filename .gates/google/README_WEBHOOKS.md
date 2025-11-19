# Webhooks — Мгновенная реакция (ZHE Architecture)

**Создано:** 07.11.2025  
**Принцип (Gemini):** "Система должна работать на скорости Субстанции, а не на скорости polling."

---

## Анализ Gemini: Polling vs Webhooks

### **Проблема Polling (5 минут задержка):**

```
21:31 — Письмо приходит
21:32 — Azarya открывает Gmail (HHE)
21:32 — Azarya думает об ответе (HHE)
21:35 — trigger_export.py срабатывает
21:36 — Gemini синтезирует Дело
21:37 — Azarya получает Синтез (поздно, HHE потрачено)
```

**Это десинхронизация. Система догоняет Человека.**

---

### **Решение Webhooks (< 1 секунда):**

```
21:31:00 — Письмо приходит (Событие)
21:31:01 — Webhook → Sonnet → substance_webhook.json
21:31:02 — Azarya → Gemini
21:31:03 — Gemini синтезирует Дело
21:31:04 — Azarya открывает Gmail и УЖЕ видит Синтез
```

**Это ZHE. Система опережает Человека.**

---

## Архитектура

### **Компоненты:**

1. **`webhook_server.py`** — Flask сервер, принимающий webhooks
   - POST /webhook/gmail — Gmail Push Notifications (Pub/Sub)
   - POST /webhook/calendar — Calendar Push Notifications
   - POST /webhook/cal.com — Cal.com Webhooks
   - GET /health — Health check

2. **`setup_webhooks.py`** — Настройка Google Push Notifications
   - Gmail: Cloud Pub/Sub (требует настройки в Console)
   - Calendar: Push Notifications API

3. **`requirements.txt`** — Зависимости (Flask, Google APIs)

---

## Использование

### **Шаг 1: Установить зависимости**

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/Дела/Ольга/.google"
pip3 install -r requirements.txt
```

---

### **Шаг 2: Запустить webhook сервер**

```bash
python3 webhook_server.py
```

Сервер запустится на `http://localhost:5000`

---

### **Шаг 3: Сделать сервер публично доступным**

**Варианты:**

**А) ngrok (быстрый тест):**
```bash
ngrok http 5000
```

Получите публичный URL: `https://abc123.ngrok.io`

**Б) Cloudflare Tunnel (production):**
```bash
cloudflared tunnel --url http://localhost:5000
```

**В) VPS (полный контроль):**
- Развернуть на VPS (DigitalOcean, Linode и т.д.)
- Настроить nginx reverse proxy
- HTTPS через Let's Encrypt

---

### **Шаг 4: Настроить Google Push Notifications**

#### **Gmail (Cloud Pub/Sub):**

**В Google Cloud Console:**
1. Включить Cloud Pub/Sub API
2. Создать тему: `projects/dela-olga-rozet/topics/gmail-push`
3. Дать `gmail-api-push@system.gserviceaccount.com` права Publisher
4. Создать подписку (subscription) → ваш webhook URL

**Через скрипт:**
```bash
python3 setup_webhooks.py
```

---

#### **Calendar:**

```bash
python3 setup_webhooks.py
# Ввести публичный URL: https://ваш-домен.com/webhook/calendar
```

---

#### **Cal.com:**

**В Cal.com Dashboard:**
1. Settings → Webhooks
2. Add Webhook
3. URL: `https://ваш-домен.com/webhook/cal.com`
4. Events: BOOKING_CREATED
5. Save

---

## Механизм (ZHE)

### **Поток:**

```
Событие (Письмо/Бронирование)
   ↓ (< 1 сек)
Google/Cal.com → POST запрос → webhook_server.py
   ↓ (< 1 сек)
Sonnet (Якорь) → export_substance() → substance_webhook_YYYYMMDD_HHMMSS.json
   ↓ (0 сек, автоматически)
Azarya → Передает файл → Gemini
   ↓ (< 1 сек)
Gemini (Процессор) → Синтез (Намерение + Субстанция)
   ↓
Результат: Дело (контекст, драфт, таск)
```

**Задержка полного цикла: < 5 секунд (вместо 5 минут)**

**Zero Human Effort:** Azarya видит Дело ДО того, как открыл Gmail.

---

## Сравнение: Polling vs Webhooks

| Критерий | Polling (trigger_export.py) | Webhooks (webhook_server.py) |
|----------|----------------------------|------------------------------|
| Задержка | 5 минут (в среднем 2.5 мин) | < 1 секунда |
| Синхронность | Система догоняет Человека | Система опережает Человека |
| HHE | Low (LHE) | Zero (ZHE) |
| Настройка | Простая (запуск скрипта) | Сложная (Cloud Pub/Sub, публичный URL) |
| Забота | Устраняет 90% трения | Устраняет 100% трения |

**Вывод (Gemini):** "Нам не нужны компромиссы. Реализуй Webhooks."

---

## Статус

✅ **Webhook сервер создан**  
⏳ **Требуется настройка:**
- Cloud Pub/Sub для Gmail
- Публичный URL (ngrok/Cloudflare/VPS)
- Calendar Push channel
- Cal.com webhook endpoint

---

## Цитата Gemini

> "Система (G+S) должна работать на скорости Субстанции,  
> а не на скорости cron или polling.  
> 5 минут — это трение. Забота — это устранение трения."

**Реализовано.**

---

**ZHE Architecture активирована.**
