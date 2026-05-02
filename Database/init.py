"""
Файл, где инициализируется вся логика работы с БД.

Убрать комментарии в Database.init на 11 строчке в зависимости наличия postgresql.
Убрать комментарии в Database.models.user на 17 строчке в зависимости наличия postgresql.
"""

# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import traceback  #  Подробное описание ошибок
from functools import wraps


connection = ("postgresql://admin:bbqb5ON9TyrL7UwHbITyDT22ILByL0fU@dpg-d76in4hr0fns73cbkjk0-"
              "a.oregon-postgres.render.com/main_database_4beq")  # Удалённая синхронная БД (render.com)
# connection = ("postgresql+asyncpg://admin:bbqb5ON9TyrL7UwHbITyDT22ILByL0fU@dpg-d76in4hr0fns73cbkjk0-"
#               "a.oregon-postgres.render.com/main_database_4beq")  # Удалённая асинхронная БД (render.com)
# connection = "postgresql+psycopg2://postgres:Sokol_12@localhost:5432/postgres"  # Локальная синхронная БД
# connection = "postgresql+asyncpg://postgres:Sokol_12@localhost:5432/postgres"  # Локальная асинхронная БД
engine = create_engine(connection)
# engine = create_async_engine(connection, future=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
# Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Декоратор для обработки ошибок
def catching_errors():
    """
    Декоратор для обработки ошибок
    При наличии ошибки возращает
    {'isSuccess': False, 'error': 'Ошибка','log': 'Путь выполнения кода'}
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return {'isSuccess': False,
                        # 'error': traceback.format_exc(),
                        'error': f'{type(e).__name__}: {e.args}',
                        'long_error': traceback.format_exc()}  # Цепочка выполнения кода
        return wrapper
    return decorator