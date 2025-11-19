# Получение CAL_API_KEY

## Шаги

1. Открой: https://app.cal.com/settings/developer/api-keys
2. Нажми **+ Create API Key**
3. Название: `olgaroset.ru Auto Sync`
4. Выбери права:
   - ✅ Read Event Types
   - ✅ Write Event Types
   - ✅ Read Bookings
   - ✅ Write Bookings
5. **Create** → скопируй ключ
6. Сохрани в `.gates/calcom/.env`:
   ```
   CAL_API_KEY=cal_live_xxxxxxxxxxxxxxxx
   ```

## Автоматическая установка

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/.gates/calcom"
echo "CAL_API_KEY=ТУТ_ТВОЙ_КЛЮЧ" > .env
```

## Проверка

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/.gates/calcom"
python3 calcom_gate.py
```

Должно показать твой username и статистику.

## GitHub Secrets (для автоматической синхронизации)

1. Открой: https://github.com/stasazaryarozet/olgaroset.ru/settings/secrets/actions
2. **New repository secret**
3. Name: `CAL_API_KEY`
4. Value: `cal_live_xxxxxxxxxxxxxxxx`
5. **Add secret**

Теперь при изменении `content.md` → автоматически обновится Cal.com.

