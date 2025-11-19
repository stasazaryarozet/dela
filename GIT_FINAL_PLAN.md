# ФИНАЛЬНЫЙ ПЛАН: Git-архитектура по высшим стандартам

**Дата:** 2025-11-19  
**Цель:** Упорядочить Git-структуру с максимальной модульностью, иерархией и доступностью

---

## Обнаруженные проблемы

### 1. `olgaroset.ru` vs `olgarozet.ru` — КОНФЛИКТ

**Проблема:**
```bash
olga/olgaroset.ru/  → github.com/stasazaryarozet/olgaroset.ru
olga/olgarozet.ru/  → github.com/stasazaryarozet/olgaroset.ru (ТОТ ЖЕ!)
```

**Это разные проекты, но один remote!**

**Содержимое:**
- `olgaroset.ru`: CACHE_BUSTING, GIT_PUSH_ISSUE, PILOT_SLOT, works/, chl/
- `olgarozet.ru`: CALCOM_DEEP_INTEGRATION, booking/, build.py, content/

**Решение:** Создать отдельный repo для `olgarozet.ru`

### 2. Вложенные `.git` без submodules

8 независимых `.git` directories нарушают иерархию.

---

## ФИНАЛЬНАЯ АРХИТЕКТУРА (Monorepo + Submodules)

### GitHub Organization:

```
stasazaryarozet/
  ├── dela                      # Корневой monorepo (СОЗДАТЬ)
  ├── olgaroset.ru              # ✅ Существует
  ├── olgarozet.ru              # СОЗДАТЬ (новый repo!)
  ├── atlas-curation            # ✅ Существует
  ├── olga-consultations        # ✅ Существует  
  ├── design-travels            # ✅ Существует
  └── github-incident-ballad    # ✅ Существует
```

### Локальная структура:

```
○/  (dela monorepo)
├── .git/                       # Корневой monorepo
├── .gitmodules                 # Конфигурация submodules
│
├── .gates/                     # Shared: доступны всем
├── .context/
├── tools/
├── KNOWLEDGE_BASE/
│
├── olga/
│   ├── DATA.yaml               # Единый источник истины
│   ├── meta_universal.py
│   │
│   ├── olgaroset.ru/           → submodule (stasazaryarozet/olgaroset.ru)
│   ├── olgarozet.ru/           → submodule (stasazaryarozet/olgarozet.ru)
│   ├── atlas-curation/         → submodule (stasazaryarozet/atlas-curation)
│   ├── consultations/          → submodule (stasazaryarozet/olga-consultations)
│   └── design-travels/         → submodule (stasazaryarozet/design-travels)
│
└── github-incident-ballad/     → submodule (stasazaryarozet/github-incident-ballad)
```

---

## ПЛАН РЕАЛИЗАЦИИ (Пошагово)

### Этап 1: Подготовка

#### 1.1. Создать недостающие GitHub repos

```bash
# Корневой monorepo
gh repo create stasazaryarozet/dela --public \
  --description "Monorepo всех проектов Дел: модульность + иерархия + общий доступ"

# Отдельный repo для olgarozet.ru
gh repo create stasazaryarozet/olgarozet.ru --public \
  --description "Альтернативная версия сайта Ольги Розет"
```

#### 1.2. Исправить remote для `olgarozet.ru`

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/olga/olgarozet.ru"
git remote set-url origin https://github.com/stasazaryarozet/olgarozet.ru.git
git push -u origin main
```

---

### Этап 2: Резервное копирование

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Создать backup текущего состояния
tar -czf ~/dela_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude='node_modules' \
  --exclude='.git' \
  .
```

---

### Этап 3: Очистка конфликтующих `.git`

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Удалить корневой .git (если есть)
[ -d .git ] && rm -rf .git

# Удалить olga/.git (конфликт с submodules)
[ -d olga/.git ] && rm -rf olga/.git

# Сохранить конфигурацию submodules проектов временно
cd olga
for dir in olgaroset.ru olgarozet.ru atlas-curation consultations design-travels; do
  if [ -d "$dir/.git" ]; then
    cp "$dir/.git/config" "$dir/.git_config_backup"
  fi
done
cd ..
```

---

### Этап 4: Инициализация корневого monorepo

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Инициализировать
git init
git remote add origin git@github.com:stasazaryarozet/dela.git

# Добавить shared infrastructure
git add .gates/ .context/ tools/ KNOWLEDGE_BASE/
git add olga/DATA.yaml olga/meta_universal.py
git add GIT_ARCHITECTURE_PLAN.md GIT_STRUCTURE_STATUS.md

# Первый коммит
git commit -m "🏗️ Initial monorepo: shared infrastructure

- .gates/: Общие интеграции (Cal.com, Telegram)
- tools/: Утилиты (sync_daemon, валидация)
- KNOWLEDGE_BASE/: База знаний
- olga/DATA.yaml: Единый источник истины
- olga/meta_universal.py: Общая логика

Модульность + Иерархия + Общий доступ по стандартам Git."

# Создать основную ветку
git branch -M main
```

---

### Этап 5: Добавление submodules

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Временно переместить существующие директории
cd olga
for dir in olgaroset.ru olgarozet.ru atlas-curation consultations design-travels; do
  [ -d "$dir" ] && mv "$dir" "${dir}.backup"
done
cd ..

mv github-incident-ballad github-incident-ballad.backup

# Добавить все как submodules
git submodule add git@github.com:stasazaryarozet/olgaroset.ru.git olga/olgaroset.ru
git submodule add git@github.com:stasazaryarozet/olgarozet.ru.git olga/olgarozet.ru
git submodule add git@github.com:stasazaryarozet/atlas-curation.git olga/atlas-curation
git submodule add git@github.com:stasazaryarozet/olga-consultations.git olga/consultations
git submodule add git@github.com:stasazaryarozet/design-travels.git olga/design-travels
git submodule add git@github.com:stasazaryarozet/github-incident-ballad.git github-incident-ballad

# Инициализировать и обновить
git submodule init
git submodule update --remote

# Коммит конфигурации
git add .gitmodules
git commit -m "🔗 Add all projects as submodules

Submodules:
- olga/olgaroset.ru (основной сайт)
- olga/olgarozet.ru (альтернативная версия)
- olga/atlas-curation
- olga/consultations (olga-consultations)
- olga/design-travels
- github-incident-ballad

Каждый модуль = независимый GitHub repo + независимое версионирование."
```

---

### Этап 6: Восстановление локальных изменений

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Скопировать незакоммиченные изменения из backup
cd olga
for dir in olgaroset.ru olgarozet.ru atlas-curation consultations design-travels; do
  if [ -d "${dir}.backup" ]; then
    rsync -av --exclude='.git' "${dir}.backup/" "$dir/"
    rm -rf "${dir}.backup"
  fi
done
cd ..

# То же для github-incident-ballad
if [ -d "github-incident-ballad.backup" ]; then
  rsync -av --exclude='.git' "github-incident-ballad.backup/" "github-incident-ballad/"
  rm -rf "github-incident-ballad.backup"
fi

# Проверить статус
git status
git submodule foreach 'git status'
```

---

### Этап 7: Пуш в GitHub

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Пуш корневого monorepo
git push -u origin main

# Убедиться, что все submodules тоже запушены
git submodule foreach 'git push origin main || git push origin master'
```

---

### Этап 8: Настройка CI/CD

Создать `.github/workflows/sync-submodules.yml`:

```yaml
name: Sync Submodules

on:
  schedule:
    - cron: '0 */4 * * *'  # Каждые 4 часа
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout with submodules
        uses: actions/checkout@v3
        with:
          submodules: recursive
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Update submodules
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git submodule update --remote --recursive
          git add .
          if ! git diff --quiet --cached; then
            git commit -m "🔄 Auto-update submodules [skip ci]"
            git push
          else
            echo "No changes to commit"
          fi
```

---

### Этап 9: Документация

Создать `README.md` корневого repo:

```markdown
# Дела (dela)

Monorepo всех проектов Азарии и Ольги Розет.

## Архитектура

**Принципы:**
- ✅ Модульность: каждый проект = отдельный GitHub repo
- ✅ Иерархия: корневой dela → submodules
- ✅ Общий доступ: shared infrastructure для всех

**Структура:**
\`\`\`
dela/
├── .gates/          # Shared integrations
├── tools/           # Shared utilities
├── KNOWLEDGE_BASE/  # Shared knowledge
├── olga/            # Проекты Ольги
│   ├── olgaroset.ru/     → submodule
│   ├── olgarozet.ru/     → submodule
│   ├── atlas-curation/   → submodule
│   ├── consultations/    → submodule
│   └── design-travels/   → submodule
└── github-incident-ballad/ → submodule
\`\`\`

## Использование

### Клонирование

\`\`\`bash
# Клонировать всё (с submodules)
git clone --recursive git@github.com:stasazaryarozet/dela.git

# Или клонировать только нужный проект
git clone git@github.com:stasazaryarozet/olgaroset.ru.git
\`\`\`

### Обновление submodules

\`\`\`bash
# Обновить все submodules
git submodule update --remote --recursive

# Обновить конкретный submodule
cd olga/olgaroset.ru
git pull origin main
\`\`\`

### Коммит изменений в submodule

\`\`\`bash
# В submodule
cd olga/olgaroset.ru
git add .
git commit -m "Update content"
git push origin main

# В корневом repo (обновить указатель)
cd ../..
git add olga/olgaroset.ru
git commit -m "Update olgaroset.ru submodule"
git push
\`\`\`

## Проекты

- **olgaroset.ru** — основной сайт Ольги Розет
  - GitHub Pages: https://stasazaryarozet.github.io/olgaroset.ru/
- **olgarozet.ru** — альтернативная версия сайта
- **atlas-curation** — курирование выставок
- **consultations** — консультации
- **design-travels** — дизайн-путешествия
- **github-incident-ballad** — эпос о GitHub Incident
  - GitHub Pages: https://stasazaryarozet.github.io/github-incident-ballad/

## Best Practices

Соответствует:
- ✅ Git Submodules (используется Linux kernel, LLVM, WebKit)
- ✅ Monorepo pattern (используется Google, Facebook)
- ✅ Модульность (каждый проект независим)
- ✅ Shared infrastructure (общий код доступен всем)

## Документация

- [Архитектура](GIT_ARCHITECTURE_PLAN.md)
- [Текущий статус](GIT_STRUCTURE_STATUS.md)
\`\`\`

---

## Тестирование

### После завершения миграции:

```bash
# 1. Клонировать на чистой машине/директории
cd /tmp
git clone --recursive git@github.com:stasazaryarozet/dela.git
cd dela

# 2. Проверить структуру
ls -la
ls -la olga/
ls -la .gates/

# 3. Проверить доступ к shared infrastructure
cd olga/olgaroset.ru
python3 -c "import sys; sys.path.insert(0, '../..'); from tools import sync_daemon; print('✓ Shared access works')"

# 4. Проверить каждый submodule
git submodule foreach 'echo "=== $name ===" && git status'

# 5. Проверить GitHub Pages
curl -I https://stasazaryarozet.github.io/olgaroset.ru/
curl -I https://stasazaryarozet.github.io/github-incident-ballad/
```

---

## Преимущества финальной архитектуры

### 1. Модульность ✅
- Каждый проект = отдельный GitHub repo
- Независимое версионирование
- Можно клонировать отдельно

### 2. Иерархия ✅
- Корневой `dela` = master
- Submodules = дочерние
- Чёткая структура зависимостей

### 3. Общий доступ ✅
- `.gates/`, `tools/`, `KNOWLEDGE_BASE/` доступны всем через relative paths
- `olga/DATA.yaml` = единый источник истины
- Imports работают: `from tools import sync_daemon`

### 4. GitHub Pages ✅
- Каждый submodule публикуется независимо
- `stasazaryarozet.github.io/olgaroset.ru/`
- Автоматическое обновление через GitHub Actions

### 5. Best Practices ✅
- Соответствует стандартам Computer Science
- Используется крупными open-source проектами
- Поддержка IDE (VS Code, JetBrains)

---

## Rollback Plan (если что-то пойдёт не так)

```bash
# Восстановить из backup
cd ~
tar -xzf dela_backup_*.tar.gz -C "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Или откатить через Git
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"
git reset --hard HEAD~1
git submodule foreach 'git reset --hard HEAD~1'
```

---

## ГОТОВ К РЕАЛИЗАЦИИ

**Следующий шаг:** Выполнить план поэтапно, начиная с Этапа 1.

**Требуется подтверждение пользователя** перед:
- Удалением `.git` directories
- Созданием новых GitHub repos
- Пушем в корневой monorepo

