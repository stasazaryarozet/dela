# Git Architecture: Оптимальная структура для проекта Дел

**Дата:** 2025-11-19  
**Цель:** Упорядочить Git-структуру по лучшим практикам Computer Science

---

## Текущая проблема

### 8 независимых репозиториев (анти-паттерн):
```
○/                              # monorepo (root)
  .git/                         # ✗ конфликт с submodules
  
  olga/
    .git/                       # ✗ несуществующий remote
    olgaroset.ru/.git/          # ✓ github.com/stasazaryarozet/olgaroset.ru
    olgarozet.ru/.git/          # ✓ github.com/stasazaryarozet/olgarozet.ru (опечатка?)
    atlas-curation/.git/        # ✗ неизвестный remote
    consultations/.git/         # ✗ неизвестный remote
    design-travels/.git/        # ✗ неизвестный remote
  
  github-incident-ballad/
    .git/                       # ✓ github.com/stasazaryarozet/github-incident-ballad
```

**Проблемы:**
1. ❌ Нарушена иерархия: вложенные `.git` в разных уровнях
2. ❌ Нет модульности: каждый проект изолирован
3. ❌ Нет общего доступа: проекты не видят друг друга
4. ❌ 5 репозиториев без remote (не синхронизируются)
5. ❌ Дублирование: `olgaroset.ru` vs `olgarozet.ru`

---

## Оптимальная архитектура (Git Best Practices)

### Вариант A: Monorepo с Submodules (рекомендую)

```
○/                                    # Master monorepo
  .git/                               # github.com/azrosyak/dela (новый)
  
  .gitmodules                         # Конфигурация submodules
  
  olga/                               # Проект Ольга (не submodule)
    olgaroset.ru/                     # → submodule
    atlas-curation/                   # → submodule
    consultations/                    # → submodule
    design-travels/                   # → submodule
  
  github-incident-ballad/             # → submodule
  
  # Shared infrastructure (доступна всем)
  .gates/
  .context/
  tools/
  KNOWLEDGE_BASE/
```

**Преимущества:**
- ✅ Единая история всего проекта
- ✅ Модули независимо версионированы
- ✅ Общая инфраструктура доступна всем
- ✅ Каждый submodule = отдельный GitHub repo
- ✅ `git clone --recursive` → всё сразу

**Как работает:**
```bash
# В корневом repo
git submodule add https://github.com/stasazaryarozet/olgaroset.ru.git olga/olgaroset.ru
git submodule add https://github.com/stasazaryarozet/github-incident-ballad.git github-incident-ballad

# Submodules указывают на конкретные коммиты
# Обновление submodule:
cd olga/olgaroset.ru
git pull origin main
cd ../..
git add olga/olgaroset.ru
git commit -m "Update olgaroset.ru to latest"
```

---

### Вариант B: Monorepo без Submodules (альтернатива)

```
○/                                    # Единый репозиторий
  .git/                               # github.com/azrosyak/dela
  
  olga/
    olgaroset.ru/                     # просто папка (не submodule)
    atlas-curation/
    consultations/
    design-travels/
  
  github-incident-ballad/
```

**Преимущества:**
- ✅ Максимальная простота
- ✅ Атомарные коммиты между проектами
- ✅ Единая история
- ✅ Общий CI/CD

**Недостатки:**
- ❌ Нет независимого версионирования модулей
- ❌ Нельзя клонировать только один проект
- ❌ GitHub Pages требует отдельных репозиториев

---

### Вариант C: Multi-repo (текущее, но исправленное)

```
# Отдельные репозитории:
github.com/stasazaryarozet/olgaroset.ru        # olga/olgaroset.ru/
github.com/stasazaryarozet/atlas-curation      # olga/atlas-curation/
github.com/stasazaryarozet/consultations       # olga/consultations/
github.com/stasazaryarozet/design-travels      # olga/design-travels/
github.com/stasazaryarozet/github-incident-ballad

# Без корневого monorepo
# Локально: все в ○/, но каждый — независимый git repo
```

**Преимущества:**
- ✅ Полная независимость проектов
- ✅ GitHub Pages работает из коробки

**Недостатки:**
- ❌ Нет общей истории
- ❌ Сложно синхронизировать изменения
- ❌ Дублирование инфраструктуры (.gates, tools)

---

## Рекомендация: Вариант A (Monorepo + Submodules)

### Структура:

```
azrosyak/dela                         # Master monorepo (новый)
├── .gitmodules
├── .gates/                           # Shared: доступны всем
├── .context/
├── tools/
├── KNOWLEDGE_BASE/
│
├── olga/
│   ├── DATA.yaml                     # Shared data
│   ├── meta_universal.py             # Shared logic
│   ├── olgaroset.ru/      → submodule (stasazaryarozet/olgaroset.ru)
│   ├── atlas-curation/    → submodule (stasazaryarozet/atlas-curation)
│   ├── consultations/     → submodule (stasazaryarozet/consultations)
│   └── design-travels/    → submodule (stasazaryarozet/design-travels)
│
└── github-incident-ballad/ → submodule (stasazaryarozet/github-incident-ballad)
```

### GitHub организация:

```
stasazaryarozet/
  ├── dela                            # Корневой monorepo (новый)
  ├── olgaroset.ru                    # Submodule 1 (существует)
  ├── atlas-curation                  # Submodule 2 (создать)
  ├── consultations                   # Submodule 3 (создать)
  ├── design-travels                  # Submodule 4 (создать)
  └── github-incident-ballad          # Submodule 5 (существует)
```

---

## План миграции

### Этап 1: Создать недостающие GitHub repos

```bash
# Через GitHub CLI
gh repo create stasazaryarozet/dela --public
gh repo create stasazaryarozet/atlas-curation --public
gh repo create stasazaryarozet/consultations --public
gh repo create stasazaryarozet/design-travels --public
```

### Этап 2: Инициализировать submodules в существующих проектах

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○/olga/atlas-curation"
git init
git remote add origin git@github.com:stasazaryarozet/atlas-curation.git
git add .
git commit -m "Initial commit: Atlas Curation"
git push -u origin main

# Повторить для consultations, design-travels
```

### Этап 3: Удалить конфликтующие .git

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Удалить корневой .git (если не нужен)
rm -rf .git

# Удалить olga/.git (конфликт с submodules)
rm -rf olga/.git

# Удалить olga/olgarozet.ru/.git (опечатка, дубликат)
# Проверить, что это действительно дубликат olgaroset.ru
```

### Этап 4: Создать корневой monorepo

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"
git init
git remote add origin git@github.com:stasazaryarozet/dela.git

# Добавить общие файлы
git add .gates/ .context/ tools/ KNOWLEDGE_BASE/ olga/DATA.yaml olga/meta_universal.py
git commit -m "🏗️ Initial monorepo: shared infrastructure"
```

### Этап 5: Добавить submodules

```bash
cd "/Users/azaryarozet/Library/Mobile Documents/com~apple~CloudDocs/○"

# Сохранить существующие проекты временно
mv olga/olgaroset.ru olga/olgaroset.ru.backup
mv github-incident-ballad github-incident-ballad.backup

# Добавить как submodules
git submodule add git@github.com:stasazaryarozet/olgaroset.ru.git olga/olgaroset.ru
git submodule add git@github.com:stasazaryarozet/atlas-curation.git olga/atlas-curation
git submodule add git@github.com:stasazaryarozet/consultations.git olga/consultations
git submodule add git@github.com:stasazaryarozet/design-travels.git olga/design-travels
git submodule add git@github.com:stasazaryarozet/github-incident-ballad.git github-incident-ballad

# Коммит конфигурации submodules
git add .gitmodules olga/ github-incident-ballad/
git commit -m "🔗 Add submodules: все проекты связаны"
git push -u origin main
```

### Этап 6: Восстановить локальные изменения

```bash
# Скопировать незакоммиченные изменения из backup
rsync -av olga/olgaroset.ru.backup/ olga/olgaroset.ru/
rm -rf olga/olgaroset.ru.backup

# Повторить для других проектов
```

---

## Best Practices

### 1. Работа с submodules

```bash
# Клонирование всего проекта
git clone --recursive git@github.com:stasazaryarozet/dela.git

# Обновление всех submodules
git submodule update --remote --recursive

# Коммит изменений в submodule
cd olga/olgaroset.ru
git add .
git commit -m "Update content"
git push origin main

# Обновить указатель в parent repo
cd ../..
git add olga/olgaroset.ru
git commit -m "Update olgaroset.ru submodule"
git push
```

### 2. Shared infrastructure

```
.gates/          # Доступны всем submodules через relative paths
  calcom/
  telegram/
  
tools/           # Общие утилиты
  sync_daemon.py
  
KNOWLEDGE_BASE/  # Общая база знаний

olga/
  DATA.yaml      # Единый источник истины для всех
  meta_universal.py
```

**Доступ из submodule:**
```python
# В olga/olgaroset.ru/build.py
import sys
sys.path.insert(0, '../..')  # Доступ к корневому monorepo
from tools import sync_daemon
from olga import meta_universal
```

### 3. GitHub Actions для monorepo

```yaml
# .github/workflows/sync-submodules.yml
name: Sync Submodules
on:
  schedule:
    - cron: '0 * * * *'  # Каждый час
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive
          token: ${{ secrets.PAT }}
      
      - name: Update submodules
        run: |
          git submodule update --remote --recursive
          git add .
          git diff --quiet || git commit -m "🔄 Auto-update submodules"
          git push
```

### 4. .gitmodules конфигурация

```ini
[submodule "olga/olgaroset.ru"]
    path = olga/olgaroset.ru
    url = git@github.com:stasazaryarozet/olgaroset.ru.git
    branch = main
    update = merge

[submodule "olga/atlas-curation"]
    path = olga/atlas-curation
    url = git@github.com:stasazaryarozet/atlas-curation.git
    branch = main

[submodule "olga/consultations"]
    path = olga/consultations
    url = git@github.com:stasazaryarozet/consultations.git
    branch = main

[submodule "olga/design-travels"]
    path = olga/design-travels
    url = git@github.com:stasazaryarozet/design-travels.git
    branch = main

[submodule "github-incident-ballad"]
    path = github-incident-ballad
    url = git@github.com:stasazaryarozet/github-incident-ballad.git
    branch = master
```

---

## Преимущества финальной архитектуры

### 1. Модульность ✅
- Каждый проект = отдельный GitHub repo
- Независимое версионирование
- Можно клонировать отдельно: `git clone stasazaryarozet/olgaroset.ru`

### 2. Иерархия ✅
- Корневой `dela` = master project
- Submodules = дочерние проекты
- Чёткая структура зависимостей

### 3. Общий доступ ✅
- `.gates/`, `tools/`, `KNOWLEDGE_BASE/` доступны всем
- `olga/DATA.yaml` = единый источник истины
- Relative imports работают

### 4. GitHub Pages ✅
- Каждый submodule публикуется отдельно
- `stasazaryarozet.github.io/olgaroset.ru/`
- `stasazaryarozet.github.io/github-incident-ballad/`

### 5. CI/CD ✅
- Автообновление submodules
- Единый workflow для всех проектов
- GitHub Actions на уровне monorepo

---

## Альтернативы Submodules

### Git Subtree (проще)
```bash
# Вместо submodule
git subtree add --prefix olga/olgaroset.ru git@github.com:stasazaryarozet/olgaroset.ru.git main

# Обновление
git subtree pull --prefix olga/olgaroset.ru git@github.com:stasazaryarozet/olgaroset.ru.git main
```

**Плюсы:**
- Проще для пользователей (не нужно `--recursive`)
- История сохраняется в monorepo

**Минусы:**
- Сложнее синхронизировать
- История "размазывается" по monorepo

### Yarn/npm workspaces (для JS проектов)
```json
// package.json
{
  "workspaces": [
    "olga/olgaroset.ru",
    "olga/consultations"
  ]
}
```

**Применимо только для JS/TypeScript проектов**

---

## Следующие шаги

### Немедленно:
1. ✅ Создать GitHub repos (через `gh repo create`)
2. ✅ Инициализировать git в `atlas-curation`, `consultations`, `design-travels`
3. ✅ Запушить начальные коммиты

### После создания repos:
4. ✅ Удалить конфликтующие `.git` directories
5. ✅ Инициализировать корневой monorepo `dela`
6. ✅ Добавить все проекты как submodules
7. ✅ Настроить GitHub Actions для auto-sync

### Тестирование:
8. ✅ `git clone --recursive` на чистой машине
9. ✅ Проверить доступ к shared infrastructure
10. ✅ Проверить GitHub Pages для всех submodules

---

## Документация

**Для пользователей (README.md корневого repo):**
```markdown
# Дела (azrosyak/dela)

Monorepo всех проектов Азарии и Ольги.

## Клонирование

\`\`\`bash
git clone --recursive git@github.com:stasazaryarozet/dela.git
cd dela
\`\`\`

## Структура

- `olga/` — проекты Ольги Розет
  - `olgaroset.ru` — основной сайт
  - `atlas-curation` — курирование выставок
  - `consultations` — консультации
  - `design-travels` — дизайн-путешествия
- `github-incident-ballad/` — эпос о GitHub Incident

## Обновление submodules

\`\`\`bash
git submodule update --remote --recursive
\`\`\`
```

---

## Резюме

**Рекомендую:** Вариант A (Monorepo + Submodules)

**Причины:**
1. ✅ Соответствует лучшим практикам Computer Science
2. ✅ Максимальная модульность
3. ✅ Чёткая иерархия
4. ✅ Общий доступ к инфраструктуре
5. ✅ Совместимость с GitHub Pages
6. ✅ Используется крупными проектами (Linux kernel, LLVM, WebKit)

**Начинаем миграцию?**

