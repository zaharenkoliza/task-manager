[project]
Лабораторная работа: FastAPI бэкенд для менеджера задач.

## Запуск локально

1. Создать и активировать виртуальное окружение Python 3.11+.
2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Применить миграции БД:

```bash
alembic upgrade head
```

4. Запустить приложение:

```bash
uvicorn app.main:app --reload --app-dir src
```

После запуска API будет доступен по адресу `http://localhost:8000`, основные ручки начинаются с префикса `/api`.

