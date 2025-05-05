**Tyutvinov_FASTAPI**

Описание проекта: управление каталогом книг с поддержкой авторов, жанров, рейтингов, аутентификации и статистики.

## Структура проекта

```text
/app
  ├── __init__.py
  ├── main.py           # Точка входа FastAPI
  ├── auth.py           # Логика аутентификации и JWT
  ├── crud.py           # CRUD-операции
  ├── schemas.py        # Pydantic-схемы
  ├── models.py         # SQLAlchemy-модели
  ├── config.py         # Настройки из .env
  ├── database.py       # Настройка подключения к БД
  ├── stats.py          # Бизнес-логика статистики
  └── test_main.py      # Тесты через TestClient
.gitignore              # Исключения для Git
.env                    # Переменные окружения (секреты)
Dockerfile              # Docker-образ
docker-compose.yml      # Сервисная комбинация Docker
books.csv               # Датасет книг
create-users.py         # Скрипт для создания тестовых пользователей
load-books.py           # Скрипт для загрузки книг из CSV
reset_db.py             # Скрипт сброса БД
requirements.txt        # Зависимости проекта
pylint.txt              # Результаты анализа Pylint
license                 # Лицензия проекта
README.md               # Описание проекта
```

## Установка и запуск

1. Скопируйте репозиторий:

```bash
git clone <url> && cd <repo>
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# Linux/macOS
source venv/bin/activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example`, укажите:

```ini
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Инициализируйте базу данных:

```bash
python reset_db.py
```

6. Загрузите книги и пользователей:

```bash
python create-users.py
python load-books.py
```

7. Запустите приложение:

```bash
uvicorn app.main:app --reload
```

8. Откройте Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Тестирование

```bash
pytest
```

## Лицензия

MIT
