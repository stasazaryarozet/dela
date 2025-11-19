# Дела — Monorepo

Централизованная архитектура всех проектов Ольги Розет с максимальной модульностью.

## Архитектура

```
dela/
├── .gates/          # Общие интеграции (Cal.com, Telegram, Google, Meta)
├── tools/           # Утилиты (sync_daemon, транскрибация, валидация)
├── KNOWLEDGE_BASE/  # База знаний (templates, reports)
├── olga/
│   ├── DATA.yaml              # Единый источник истины
│   ├── meta_universal.py      # Общая логика для всех проектов
│   ├── olgaroset.ru/          # Submodule: основной сайт
│   ├── olgarozet.ru/          # Submodule: альтернативная версия
│   ├── atlas-curation/        # Submodule: кураторство
│   ├── consultations/         # Submodule: консультации
│   └── design-travels/        # Submodule: путешествия дизайна
└── github-incident-ballad/    # Submodule: документация инцидентов

## Принципы

**Модульность:** Каждый проект = независимый GitHub repo + независимый git history  
**Иерархия:** Общие ресурсы (.gates, tools) доступны всем проектам  
**Доступность:** Полная взаимосвязь через DATA.yaml и meta_universal.py  
**Безопасность:** Все credentials в .gitignore, не в истории  

## Использование

### Клонирование с submodules
```bash
git clone --recursive git@github.com:stasazaryarozet/dela.git
```

### Обновление submodules
```bash
git submodule update --remote --merge
```

### Работа с отдельным проектом
```bash
cd olga/olgaroset.ru
git checkout -b feature/new-page
# ... изменения ...
git commit -m "feat: новая страница"
git push origin feature/new-page
```

### Работа с shared ресурсами
```bash
# Изменения в .gates/ или tools/ доступны всем проектам
cd .gates/calcom
vim calcom_gate.py
git add calcom_gate.py
git commit -m "fix: обработка пустых слотов"
git push origin main
```

## Стандарты

- **Computer Science:** Git Submodules для модульности
- **Best Practices:** Каждый submodule = отдельный repo с полным версионированием
- **GitHub Documentation:** Следуем официальным рекомендациям по monorepo
- **Безопасность:** Секреты только локально, никогда в Git истории

## Структура данных

`olga/DATA.yaml` — единый источник для:
- Контактов
- Событий
- Цен
- Описаний

Все проекты читают из DATA.yaml → конгруэнтность гарантирована.

---

**Модульность + Иерархия + Полный доступ = Максимальная архитектурная чистота**
