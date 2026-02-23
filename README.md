## Лабораторная работа №1 — Task Manager

Краткое описание: монорепозиторий с **backend на FastAPI** и **frontend на React/Vite** для управления задачами. Сервер и клиент общаются по REST, данные хранятся в **PostgreSQL**, есть модульные тесты и CI-пайплайн на GitHub Actions.

### Стек
- **Backend**: FastAPI, SQLAlchemy (async, PostgreSQL), Pydantic v2, Pytest (+pytest-asyncio, httpx, pytest-cov).
- **Frontend**: React 18, TypeScript, Vite, Vitest + Testing Library.
- **БД**: PostgreSQL (asyncpg), автоматическое создание таблиц и заполнение справочников статусов/приоритетов из JSON.
- **CI**: GitHub Actions (4 job’а для backend и frontend).

### Соответствие требованиям ЛР №1
1. **DevOps и Git**
   - Код организован в виде репозитория Git (`backend/`, `frontend/`), используется GitHub для хостинга и CI.
2. **RESTful сервис + БД**
   - Реализован REST API для сущности `Task` (полный CRUD) и справочников:
     - `GET /api/tasks` — список задач с фильтрами по статусу, приоритету и интервалу времени.
     - `GET /api/tasks/{id}`, `POST /api/tasks`, `PATCH /api/tasks/{id}`, `DELETE /api/tasks/{id}` (soft delete).
     - `GET /api/tasks/statuses`, `GET /api/tasks/statuses/{id}` — детерминированный список статусов (`To Do`, `In Progress`, `Done`).  
     - `GET /api/tasks/priorities`, `GET /api/tasks/priorities/{id}` — приоритеты (`High`, `Normal`, `Low`).
   - БД: PostgreSQL, доступ через async SQLAlchemy, модели `Task`, `TaskStatus`, `TaskPriority`, автоматический сидинг из `backend/seeders/*.json`.
3. **Клиентское веб-приложение**
   - Frontend (`frontend/`) получает данные от backend по REST (`/api/...`), реализует формы создания/редактирования задач, фильтрацию по статусу и приоритету, отображение списка задач.
4. **Модульные тесты**
   - Backend: тесты для конфигурации, моделей, схем и всех REST-эндпоинтов (`backend/tests/*`), включая проверки фильтрации, soft delete и валидации входных данных.
   - Frontend: компонентные и API-тесты на Vitest/Testing Library (TaskList, TaskFilters, TaskFormModal, mock API).
5. **CI с отдельными job’ами для backend и frontend**
   - Файл CI: `.github/workflows/ci.yml`.
   - **Backend**:
     - `backend-build` — сборка: установка зависимостей, компиляция исходников (`python -m compileall src`).
     - `backend-test` — сервис PostgreSQL в контейнере + прогон Pytest с покрытием (`pytest --cov=src/app`).
     - Дополнительно (необязательные): `backend-lint` (Ruff) и `backend-format-check` (Black) — не блокируют пайплайн.
   - **Frontend**:
     - `frontend-build` — установка npm-зависимостей и `npm run build`.
     - `frontend-test` — `npm run test` (Vitest).


