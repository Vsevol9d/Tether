"""
Файл, где инициализируется вся логика работы с БД.

Убрать комментарии в Database.init на 11 строчке в зависимости наличия postgresql.
Убрать комментарии в Database.models.user на 17 строчке в зависимости наличия postgresql.
"""
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import traceback  #  Подробное описание ошибок
from functools import wraps

connection = ("postgresql://super_admin:D6xOVkD3GEk6q7ZIhlPGRspFY40v4mZf@dpg-d7r3olnlk1mc73cuqv4g-a"
              ".oregon-postgres.render.com/communicator_kzeo") # Удалённая синхронная БД (render.com)
# connection = ("postgresql+asyncpg://super_admin:D6xOVkD3GEk6q7ZIhlPGRspFY40v4mZf@dpg-d7r3olnlk1mc73cuqv4g-a"
#               ".oregon-postgres.render.com/communicator_kzeo") # Удалённая асинхронная БД (render.com)

# connection = ("postgresql://super_admin:D6xOVkD3GEk6q7ZIhlPGRspFY40v4mZf@dpg-d7r3olnlk1mc73cuqv4g-a"
#               "/communicator_kzeo") # Удалённая синхронная БД. Доступно только для сервера в render.com
# connection = ("postgresql+asyncpg://super_admin:D6xOVkD3GEk6q7ZIhlPGRspFY40v4mZf@dpg-d7r3olnlk1mc73cuqv4g-a"
#               "/communicator_kzeo") # Удалённая асинхронная БД. Доступно только для сервера в render.com

# connection = "postgresql+psycopg2://postgres:Sokol_12@localhost:5432/postgres"  # Локальная синхронная БД
# connection = "postgresql+asyncpg://postgres:Sokol_12@localhost:5432/postgres"  # Локальная асинхронная БД

# engine = create_async_engine(connection)
# Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

engine = create_engine(connection)
Session = sessionmaker(bind=engine)


Base = declarative_base()

# Декоратор для обработки ошибок
def catching_errors(commit: bool = False):
    """
    Декоратор для обработки ошибок
    При наличии ошибки возращает
    {'isSuccess': False, 'error': 'Ошибка','log': 'Путь выполнения кода'}
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if commit: args[0].session.commit()  # args[0] == self в вызываемой функции

                return {'isSuccess': True, 'data': result}
            except Exception as e:
                if commit: args[0].session.rollback()
                return {
                    'isSuccess': False,
                    # 'error': traceback.format_exc(),
                    'error': f'{type(e).__name__}: {e.args}',
                    'long_error': traceback.format_exc()  # Цепочка выполнения кода
                }
        return wrapper
    return decorator