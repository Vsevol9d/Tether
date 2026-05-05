"""
Методы для изменения структуры БД
Для работы сервера или UI этот файл не предназначен
"""

from Database.init import Base, engine

def CREATE_ALL_TABLE():
    from Database.models.users import Users
    from Database.models.chats import Chats
    from Database.models.participants import Participants
    from Database.models.messages import Messages
    from Database.models.friends import Friends
    Base.metadata.create_all(engine)  # Создание всех ещё не созданных таблиц

def DROP_ALL():
    # Удаление всех таблиц. :)
    from sqlalchemy import MetaData
    metadata = MetaData()
    metadata.reflect(bind=engine)        # загрузить существующие таблицы
    metadata.drop_all(bind=engine)      # удалить все отражённые таблицы

def ADD_COLUMN(model, column):
    # Добавить колонку в таблицу users
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text(f"ALTER TABLE {model} ADD COLUMN {column}"))
        # conn.execute(text("ALTER TABLE chats ADD COLUMN id_last_mes INTEGER DEFAULT 0;"))

        # Присваивание NOT NULL
        # conn.execute(text("ALTER TABLE users ALTER COLUMN password SET NOT NULL;"))
        conn.commit()

# DROP_ALL()
# CREATE_ALL_TABLE()