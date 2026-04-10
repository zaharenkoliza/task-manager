# Лабораторная работа №4: Безопасность, SonarCloud, Argo CD, Telegram

## Цели работы

1. Изучить лучшие практики безопасности DevOps.
2. Настроить SonarCloud — статический анализ кода + покрытие тестами ≥ 80%.
3. CI не проходит если Quality Gate провален или покрытие < 80%.
4. Настроить Argo CD — автоматический деплой в Kubernetes при пуше в main.
5. Telegram бот — уведомления о статусе каждого CI/CD job.

---

## Часть 1: SonarCloud

### Шаг 1. Зарегистрироваться в SonarCloud

1. Открой [sonarcloud.io](https://sonarcloud.io)
2. Войди через **GitHub**
3. Создай организацию → выбери свой GitHub аккаунт
4. Импортируй репозиторий `task-manager`
5. Создай проект — выбери **With GitHub Actions**

### Шаг 2. Получить SONAR_TOKEN

В SonarCloud:
**My Account → Security → Generate Token**
- Name: `github-actions`
- Type: `Project Analysis Token`
- Скопируй токен

### Шаг 3. Добавить секрет в GitHub

GitHub → репозиторий → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `SONAR_TOKEN`
- Value: токен из SonarCloud

### Шаг 4. Обновить sonar-project.properties

Открой `backend/sonar-project.properties` и замени:
```
sonar.projectKey=YOUR_ORG_task-manager
sonar.organization=YOUR_ORG
```

На реальные значения из SonarCloud (видны на странице проекта → **Information**).

### Шаг 5. Настроить Quality Gate в SonarCloud

SonarCloud → проект → **Quality Gates → Create**

Условия (CI провалится если любое из них нарушено):
- Coverage < 80%
- Reliability Rating worse than A
- Security Rating worse than A
- Maintainability Rating worse than A

После создания → **Set as Default** для проекта.

### Как это работает

```
pytest --cov-fail-under=80   ← CI упадёт если покрытие < 80%
         ↓
coverage.xml                 ← отчёт отправляется в SonarCloud
         ↓
Quality Gate                 ← если не прошёл — job sonarcloud-analysis падает
         ↓
push-to-registry             ← не запустится если sonarcloud упал
```

---

## Часть 2: Argo CD

### Шаг 1. Установить Argo CD в кластер

```bash
# Создать namespace
kubectl create namespace argocd

# Установить Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Ждать пока всё поднимется (~2-3 минуты)
kubectl get pods -n argocd -w
```

Все поды должны стать `Running`.

### Шаг 2. Получить доступ к Argo CD UI

```bash
# Дать Argo CD внешний IP
kubectl patch service argocd-server -n argocd -p '{"spec":{"type":"LoadBalancer"}}'

# Ждать IP
kubectl get service argocd-server -n argocd
```

Открой `http://<EXTERNAL-IP>` в браузере.

### Шаг 3. Войти в Argo CD

```bash
# Получить начальный пароль admin
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

Логин: `admin`
Пароль: из команды выше

### Шаг 4. Применить Application manifest

```bash
kubectl apply -f k8s/argocd/application.yaml
```

### Шаг 5. Проверить синхронизацию

В Argo CD UI появится приложение `task-manager`. Статус должен стать **Synced** и **Healthy**.

### Как это работает

```
git push → GitHub → Argo CD (каждые 3 минуты проверяет репо)
                          ↓
            Обнаружил изменения в k8s/
                          ↓
            kubectl apply автоматически
                          ↓
            Кластер обновлён
```

Argo CD сам следит за `k8s/` директорией (кроме `monitoring/` и `argocd/`) и применяет изменения без ручных команд.

---

## Часть 3: Telegram бот

### Шаг 1. Создать бота

1. Открой Telegram → найди **@BotFather**
2. Отправь `/newbot`
3. Введи имя бота (например `TaskManagerCIBot`)
4. Введи username бота (например `task_manager_ci_bot`)
5. Скопируй **токен** (вида `1234567890:ABCdef...`)

### Шаг 2. Получить Chat ID

1. Напиши своему боту любое сообщение
2. Открой в браузере:
```
https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/getUpdates
```
3. В ответе найди `"chat":{"id": 123456789}` — это твой Chat ID

### Шаг 3. Добавить секреты в GitHub

GitHub → **Settings → Secrets and variables → Actions**

| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | токен от BotFather |
| `TELEGRAM_CHAT_ID` | числовой ID чата |

### Как это работает

Job `notify-telegram` запускается **всегда** (`if: always()`), даже если другие jobs упали. Он отправляет сообщение с результатами каждого job:

```
Task Manager CI/CD

Репозиторий: zaharenkoliza/task-manager
Ветка: main
Коммит: abc1234...
Автор: zaharenkoliza

Результаты jobs:
Lint: ✅
Format: ✅
Tests (покрытие ≥80%): ✅
SonarCloud: ✅
Push to Registry: ✅
```

---

## Итоговый пайплайн CI/CD

```
push в main
    │
    ├── backend-lint
    ├── backend-format-check
    │       │
    │   backend-test (pytest --cov-fail-under=80)
    │       │
    │   ┌───┴────────────────┐
    │   │                    │
    │ backend-build    sonarcloud-analysis
    │   │                    │
    │ frontend-test          │
    │   │                    │
    │ frontend-build         │
    │   └─────────┬──────────┘
    │             │
    │      push-to-registry (только main)
    │             │
    └─────────────┴── notify-telegram (всегда)
                              │
                         Telegram сообщение
                         
                    + Argo CD автоматически
                    подтягивает k8s/ изменения
```

---

## Структура изменений

```
task-manager/
├── .github/workflows/ci.yml     ← добавлены: sonarcloud-analysis, notify-telegram
│                                   обновлён: backend-test (coverage xml + fail-under=80)
│                                   обновлён: push-to-registry (depends on sonarcloud)
├── backend/
│   └── sonar-project.properties ← конфиг SonarCloud
└── k8s/
    └── argocd/
        └── application.yaml     ← Argo CD Application
```
