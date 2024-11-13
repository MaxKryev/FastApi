import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from dotenv import load_dotenv

"""Параметры для подключения к БД"""

load_dotenv()
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_test_name = os.getenv("DB_TEST_NAME")
db_test_host = os.getenv("DB_TEST_HOST")
db_test_port = os.getenv("DB_TEST_PORT")


"""Создание асинхронного движка для удаленного сервера"""

async_engine = create_async_engine(
    url=f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}",
    echo=False,
    pool_size=10,
    max_overflow=15
)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


"""Создание асинхронного движка для тестовой БД"""

# async_engine = create_async_engine(
#         url=f"postgresql+asyncpg://{db_user}:{db_pass}@{db_test_host}:{db_test_port}/{db_test_name}",
#         echo=False,
#         pool_size=10,
#         max_overflow=15
#     )
#
# async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)