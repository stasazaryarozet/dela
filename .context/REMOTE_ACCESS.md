# iPhone ↔ MacBook: Максимальная интеграция

## iPhone → MacBook (управление)

### SSH доступ

**На MacBook (один раз):**

```bash
# 1. Включить Remote Login
sudo systemsetup -setremotelogin on

# 2. Узнать IP
ipconfig getifaddr en0

# 3. Создать SSH ключ для iPhone (опционально, для безопасности)
ssh-keygen -t ed25519 -f ~/.ssh/iphone_key
cat ~/.ssh/iphone_key.pub >> ~/.ssh/authorized_keys
```

**На iPhone (Termius/Shortcuts):**

SSH to: `azaryarozet@192.168.x.x` (IP MacBook)

---

### Shortcuts с SSH

**Shortcut "Дела: Execute on Mac":**

1. SSH to MacBook
2. Run: `bash "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/Дела/.context/actions.sh"`
3. Show output

**Shortcut "Дела: Export Substance":**

1. SSH to MacBook
2. Run: `cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/Дела" && python3 .gates/google/export_substance.py`
3. Result syncs via iCloud → iPhone sees updated substance_latest.json

---

## MacBook → iPhone (управление)

### Shortcuts через URL Scheme

**На MacBook:**

```bash
# Запустить Shortcut на iPhone
shortcuts://run-shortcut?name=ДелаStatus

# Через SSH (если jailbreak или Shortcuts automation)
# Или через Apple Script + Continuity
```

### Push уведомления

**Webhook на MacBook → Pushover/Telegram → iPhone:**

```python
# webhook_server.py
@app.route('/webhook/gmail')
def gmail_webhook():
    export_substance()
    
    # Уведомление на iPhone
    send_to_telegram(chat_id=AZARYA_CHAT_ID, text="New email: {subject}")
    # ИЛИ
    pushover(message="New email", priority=1)
```

---

## Максимальная интеграция

### iPhone может:

✅ Читать все файлы Дел (iCloud Drive)
✅ Запускать скрипты на MacBook (SSH)
✅ Создавать интенции (запись в from_multitool_intentions.txt)
✅ Выполнять мои действия (actions.sh через SSH)
✅ Публиковать контент (copy from content_ready.txt)
✅ Видеть Substance (substance_latest.json)

### MacBook может:

✅ Отправлять уведомления на iPhone (Telegram/Pushover)
✅ Обновлять файлы для iPhone (iCloud sync)
✅ Реагировать на интенции с iPhone (file watcher)
✅ Запускать Shortcuts на iPhone (URL schemes)

---

## Настройка (5 минут)

### 1. Включить Remote Login на Mac

```bash
sudo systemsetup -setremotelogin on
systemsetup -getremotelogin  # проверка
```

### 2. Узнать IP MacBook

```bash
ipconfig getifaddr en0  # WiFi
# ИЛИ
ipconfig getifaddr en1  # Ethernet
```

### 3. Создать Shortcuts на iPhone

**Установить Termius** (SSH client) или использовать встроенные Shortcuts с SSH

**Создать shortcuts по инструкции из MULTITOOL_SHORTCUTS.md**

### 4. Тест

**На iPhone:**
- Запустить "Дела Status" → должен показать 27.3%
- Запустить "Дела Execute on Mac" → должен запустить actions.sh

---

## Результат

**iPhone = пульт управления Делами**
**MacBook = сервер выполнения**
**iCloud = синхронизация состояния**

**Максимальная двусторонняя интеграция.**
