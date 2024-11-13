# FastAPI Documents Manager

Это приложение предоставляет API для управления документами с использованием FastAPI. 

## Особенности
- Хранение данных документов в базе данных PostgreSQL.
- Возможность загрузки, чтения, удаления новых документов в базе данных PostgreSQL.
- Использована библиотка tesseract для выделения текста из загруженных изображений и сохранение его в базе данных PostgreSQL.
- Модели базы данных: Document и DocumentText.
- Механизм фоновых задач с использованием Celery и RabbitMQ.
- Миграции базы данных с использованием Alembic.
- Документация API через встроенные интерфейсы Swagger UI и ReDoc.
- Контейнеризация с использованием Docker и docker-compose.

## Требования
- Python 3.12
- PostgreSQL
- Docker
- RabbitMQ (для Celery)
- Tesseract

## Установка

1. Клонируйте репозиторий:
        git clone """ЗДЕСЬ БУДЕТ ССЫЛКА НА МОЙ GITHUB, ЕЩЕ НЕ ЗАЛИВАЛ"""
    

2. Установите зависимости:
        pip install -r requirements.txt


3. Настройка Docker:
    Убедитесь, что у вас установлен Docker и Docker Compose. Если нет, установите их с официальных сайтов.


4. Запуск с использованием Docker Compose:
    Требуемые переменные и данные авторизации в приложении находятся в файле .env


5. Запустите контейнеры с помощью Docker Compose:
        docker-compose up --build
    

    Это запустит:
    - FastAPI приложение (порт 8000).
    - PostgreSQL базу данных (порт 5432).
    - pgAdmin4 СУБД (порт 8080).
    - RabbitMQ (порт 5674).
    - Celery для фоновых задач.

6. Приложение будет доступно по адресу:
    
    http://0.0.0.0:8000/documents

    Документация API доступна по следующим ссылкам:
    - Swagger UI: http://0.0.0.0:8000/docs
    - ReDoc UI: http://0.0.0.0:8000/redoc

## Структура проекта

```plaintext
.
├── app/
│   ├── __init__.py
│   ├── main.py               # Главный файл с FastAPI приложением
│   ├── endpoints.py          # Edpoints приложения
│   ├── tasks.py              # Фоновые задачи Celery
│   └── schemas.py            # Модели валидации данных
├── database/  
│   ├── __init__.py
│   ├── config.py             # Настройка подключения к БД
│   ├── models.py             # Модели таблиц БД
│   └── sessions.py           # Создание сессий для работы с БД
├── documents/                # Директория с загруженными файлами  
├── migrations/               # Директория миграций alembic  
├── tests/                    # Директория с тестами
│   ├── documents/            # Директория с загруженными файлами тестов
│   ├── conftest.py           # Настройка тестов (формирование фикстур)
│   ├── test_database.py      # Тест создания таблиц в БД
│   ├── test_delete.py        # Тест на удаление файла
│   ├── test_upload_doc.py    # Тест на загрузку файла
│   └── Кот.jpeg              # Документ используемый в тестах
├── .env                      # Файл с переменными окружения
├── alembic.ini               # Файл инициализации alembic
├── docker-compose.yml        # Docker Compose файл
├── Dockerfile                # Dockerfile для приложения
├── pytest.ini                # Файл инициализации тестов
├── README.md                 # Этот файл
└── requirements.txt          # Список зависимостей