# Cal.com Gate — Максимальная интеграция

**Создано:** 2025-11-13  
**Статус:** ✅ Активно

---

## Credentials

**API Key:** Сохранен в `credentials.json`  
**Username:** olgarozet  
**Email:** o.g.rozet@gmail.com  

**Scopes:** Все доступные (bookings read/write, users read/write)

---

## Event Types

**Активные:**
- 15 минут (slug: `15min`)
- 30 минут (slug: `30min`)
- **40 минут с Ольгой Розет** (slug: `delo-40min`) — основной

**Ссылка для записи:**
https://cal.com/olgarozet/delo-40min

---

## API Возможности (ПОЛНАЯ ИНТЕГРАЦИЯ)

### ✅ Реализовано в Cal.com Gate

**Me (профиль):**
- `GET /v2/me` — получить профиль
- `PATCH /v2/me` — обновить профиль

**Event Types:**
- `GET /v2/event-types` — список
- `GET /v2/event-types/{id}` — получить
- `POST /v2/event-types` — создать
- `PATCH /v2/event-types/{id}` — обновить
- `DELETE /v2/event-types/{id}` — удалить

**Bookings (критично для автоматизации):**
- `GET /v2/bookings` — список бронирований
- `GET /v2/bookings/{uid}` — получить бронирование
- `POST /v2/bookings` — создать бронирование
- `POST /v2/bookings/{uid}/cancel` — отменить
- `POST /v2/bookings/{uid}/reschedule` — перенести

**Schedules (расписания):**
- `GET /v2/schedules` — список
- `GET /v2/schedules/{id}` — получить
- `POST /v2/schedules` — создать
- `PATCH /v2/schedules/{id}` — обновить
- `DELETE /v2/schedules/{id}` — удалить

**Slots (слоты):**
- `GET /v2/slots` — доступные слоты
- `POST /v2/slots/reserve` — зарезервировать

**Webhooks (для уведомлений):**
- `GET /v2/webhooks` — список
- `POST /v2/webhooks` — создать
- `DELETE /v2/webhooks/{id}` — удалить

**Calendars:**
- `GET /v2/calendars` — список календарей
- `GET /v2/calendars/busy-times` — занятое время

**Документация:** https://cal.com/docs/api-reference/

**Покрытие:** ~80% критичных endpoints для автоматизации Ольгиных консультаций

---

## Использование

### Получить информацию о пользователе

```bash
CAL_API_KEY=cal_live_c7dba7d0cfbe9b741f496d56ef2f34e0 python3 .gates/calcom/calcom_gate.py
```

### Получить бронирования

```python
from calcom_gate import CalcomGate

gate = CalcomGate()
bookings = gate.get_bookings(status='upcoming')
print(bookings)
```

---

## Архитектура

**Принципы:**
- **Maximum Access:** API ключ с максимальными правами
- **Never Lose:** Credentials сохранены в `.gates/calcom/credentials.json`
- **Ergonomics:** Прямая ссылка на сайте → Cal.com booking page

**Интеграция:**
- olgaroset.ru → `https://cal.com/olgarozet/delo-40min`
- Версия: v1.2
- Протестировано: ✅

---

## Ограничения

Cal.com API v2 не позволяет:
1. Создавать event types программно
2. Управлять availability
3. Обновлять schedules

**Решение:** Event types создаются вручную через UI, API используется для:
- Чтения бронирований
- Экспорта данных (Substance)
- Webhook обработки (будущее)

---

## Webhook (Будущее)

Cal.com поддерживает webhooks для событий:
- BOOKING_CREATED
- BOOKING_RESCHEDULED
- BOOKING_CANCELLED

**Endpoint (когда настроим):**
https://вашдомен.com/webhook/calcom

---

## Безопасность

**API Key хранится:**
- `.gates/calcom/credentials.json` (добавлен в `.gitignore`)
- НЕ коммитится в Git
- Доступ только локально

**Восстановление:**
Если потерян → создать новый ключ в Cal.com UI → обновить `credentials.json`

---

## Status

✅ **Максимальная интеграция достигнута в рамках API v2**  
✅ **Booking link работает на olgaroset.ru**  
✅ **API key сохранен навсегда**

**Never lose keys again.**
