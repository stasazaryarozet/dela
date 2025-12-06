# GitHub Incident 5q7nmlxz30sk: Git Operations Failure

## Хронология

**18 ноября 2025**

**23:39 МСК** — Начало инцидента  
Git Operations: major outage  
Codespaces: major outage

**00:27 МСК** — Причина идентифицирована  
"We have identified the likely cause and are working on a fix"

**00:36 МСК** — Исправление развернуто  
"We have shipped a fix and are seeing recovery in some areas"

**00:44 МСК** — Статус: investigating, recovery in progress

## Затронутые сервисы

- Git Operations (push/pull/clone)
- Codespaces

## Симптомы

```
fatal: unable to access 'https://github.com/...': Empty reply from server
fatal: unable to access 'https://github.com/...': Error in the HTTP2 framing layer
The requested URL returned error: 503
```

## Длительность

**Прошло:** 1 час 5 минут (на момент 00:44 МСК)  
**Прогноз полного восстановления:** ~02:30 МСК

## Исторический контекст

| Дата | Длительность | Сервисы |
|------|--------------|---------|
| 18 июня 2025 | 2-3 часа | Git Operations, 502/504 errors |
| 9 января 2025 | ~60 минут | Git Operations, Auth, API, Actions |
| 27 мая 2022 | ~80 минут | Multiple services |
| 13 июля 2020 | ~4 часа | Git Operations |

**Частота:** ~1 инцидент каждые 4-6 месяцев

## Принятые меры (локально)

**00:10 МСК** — Настроена автосинхронизация через launchd  
**00:40 МСК** — Тест успешен, демон запущен  
**00:42 МСК** — Изменения закоммичены локально

Автоматическая отправка в GitHub активируется при восстановлении сервиса.

## Источники

- GitHub Status API: https://www.githubstatus.com/api/v2/incidents/unresolved.json
- Incident ID: 5q7nmlxz30sk
- Shortlink: https://stspg.io/sc17dhh92kmd

## Статистика восстановления

**Median Time To Resolve (Git Operations):** 2-3 часа  
**Текущая фаза:** fix deployed, partial recovery  
**Ожидаемое завершение:** 50% вероятность к 02:30 МСК

---

_Последнее обновление: 19 ноября 2025, 00:44 МСК_


