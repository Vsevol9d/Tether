"""
Этот файл нужен для создания подсказок при вызове основных функций
"""

from Database.methods.basic_methods import BasicMethods
from Database.methods.init import Users, Chats, Participants, Messages, Friends
from Database.init import catching_errors
from sqlalchemy.orm import Session
from typing import Any, Literal
from sqlalchemy import text

class UsersQueries(BasicMethods[Users]):
    __AttrName = Literal["name", "username", "lastname", "birthday", "avatar_url",
    "last_time_online", "password", "phone", "email"]

    def __init__(self, session: Session):
        super().__init__(session, Users)

    # Чтобы были подсказки
    def add(self, name: str, username: str, password: str, lastname: str = None, birthday: str = None,
            avatar_url: str = None, phone: str | int = None, email: str = None, last_time_online: str = None) -> dict:

        # Получение следующего id
        next_id = self.session.execute(text(f"SELECT nextval('users_id_seq')")).fetchone()[0]
        return super().add(id=next_id, name=name, username=username, lastname=lastname, last_time_online=last_time_online,
                           birthday=birthday, avatar_url=avatar_url, phone=phone, email=email, password=password)

    def update(self, id: int, attr_name: __AttrName, value: Any) -> dict:
        return super().update(id=id, attr_name=attr_name, value=value)


class ChatsQueries(BasicMethods[Chats]):
    def __init__(self, session: Session):
        super().__init__(session, Chats)  # Инициализация базовых четырёх методов

    def add(self, name: str, avatar_url: str = None, type: str = None) -> dict:
        # Получение следующего id
        next_id = self.session.execute(text(f"SELECT nextval('chats_id_seq')")).fetchone()[0]

        # 1. Создание sequence, если его не существует (idempotent)
        self.session.execute(text(f"CREATE SEQUENCE IF NOT EXISTS mes_seq_{next_id} START 1"))

        return super().add(name=name, avatar_url=avatar_url, type=type, id=next_id)



class ParticipantsQueries(BasicMethods[Participants]):
    def __init__(self, session: Session):
        super().__init__(session, Participants)

    def add(self, chat_id: int, user_id: int, role: str = None) -> dict:
        return super().add(chat_id=chat_id, user_id=user_id, role=role)

    def update(self, chat_id: int, user_id: int, attr_name: str, value: Any) -> dict:
        return super().update([chat_id, user_id], attr_name, value)

    def delete(self, chat_id: int, user_id: int) -> dict:
        return super().delete([chat_id, user_id])


class MessagesQueries(BasicMethods[Messages]):
    def __init__(self, session: Session):
        super().__init__(session, Messages)

    @catching_errors()
    def add(self, chat_id: int, user_id: int, type: str = None, mes_text: str = None, file_id: int = None) -> dict:
        """
        Специальный add для сообщений.
        Получает локальный id = nextval(mes_seq_<chat_id>) и вставляет запись.
        """

        seq_name =  f"mes_seq_{chat_id}"

        # 2. Получение максимального id +1 для соответствующего сообщения чата
        # Операция быстрая за счёт получения значения встроенного счётчика
        local_id = self.session.execute(text(f"SELECT nextval('{seq_name}')")).fetchone()[0]

        # 3. Добавление строки
        msg_data = {
            "id": local_id,
            "type": type,
            "text": mes_text,
            "file_id": file_id,
            "chat_id": chat_id,
            "user_id": user_id
        }

        self.session.add(Messages(**msg_data))

        return {'isSuccess': True, 'data': msg_data}

class FriendsQueries(BasicMethods[Friends]):
    def __init__(self, session: Session):
        super().__init__(session, Friends)

    def add(self, user_id_1: int, user_id_2: int, level_relationships: int = None) -> dict:
        if user_id_1 > user_id_2: user_id_1, user_id_2 = user_id_2, user_id_1
        return super().add(user_id_1=user_id_1, user_id_2=user_id_2, level_relationships=level_relationships)

    def delete(self, user_id_1: int, user_id_2: int) -> dict:
        if user_id_1 > user_id_2: user_id_1, user_id_2 = user_id_2, user_id_1
        return super().delete(user_id_1, user_id_2)