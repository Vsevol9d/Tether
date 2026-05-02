# Инициализация классов таблиц и классов с методами
from Database.methods.configuring_classes import (UsersRequests, ChatsRequests,
                                                  ParticipantsRequests, MessagesRequests, FriendsRequests)
from Database.methods.init import Users, Chats, Participants, Messages, Friends
from Database.methods.basic_methods import BasicMethods
from Database.init import catching_errors
from sqlalchemy import select, text

# Главный класс - через него осуществляется работа с методами
class DataBase(BasicMethods):
    def __init__(self, session):
        super().__init__(session)

        self.users = UsersRequests(session)
        self.chats = ChatsRequests(session)
        self.participants = ParticipantsRequests(session)
        self.messages = MessagesRequests(session)
        self.friends = FriendsRequests(session)

    @catching_errors()
    def select_all_users_by_chat_id(self, chat_id: int) -> dict:
        """
        Получение всех пользователей, которые состоят в чате с chat_id = chat_id

        :param chat_id: id чата
        :return: словарь, где isSuccess = True, если ошибок нет, иначе False.
        В data храниться список словарей с инфо об пользователях
        """

        query = select(Users).join(Users.participants).where(Participants.chat_id == chat_id)
        raw_data = self.session.execute(query).scalars().all()
        structured_data = self._get_dict(raw_data)
        return {'isSuccess': True, 'data': structured_data}

    @catching_errors()
    def select_id_name_by_username(self, username: str) -> dict:
        data = self.session.execute(select(Users.id, Users.name).where(Users.username == username)).mappings().one_or_none()
        return {'isSuccess': True, 'data': dict(data)}

    @catching_errors()
    def select_user_name_by_id(self, id: int) -> dict:
        data = self.session.execute(select(Users.name).where(Users.id == id)).mappings().one_or_none()
        return {'isSuccess': True, 'data': dict(data)}

    @catching_errors()
    def select_all_chats_by_id_user(self, user_id: int) -> dict:
        """
        Получение всех чатов, в которых состоит пользователь с id = user_id

        :param user_id: id нужного пользователя
        :return: Список словарей, где словарь - данные о чате
        """

        query = select(Chats).join(Chats.participants).where(Participants.user_id == user_id)
        raw_data = self.session.execute(query).scalars().all()
        structured_data = self._get_dict(raw_data)
        return {'isSuccess': True, 'data': structured_data}

    @catching_errors()
    def select_all_messages_by_chat_id(self, chat_id: int) -> dict:
        """
        Получение всех сообщений, которые написаны в чате с chat_id = chat_id

        :param chat_id: id чата
        :return: словарь, где isSuccess = True, если ошибок нет, иначе False.
        В data храниться список словарей с инфо об пользователях
        """

        query = select(Messages).where(Messages.chat_id == chat_id)
        raw_data = self.session.execute(query).scalars().all()
        structured_data = self._get_dict(raw_data)
        return {'isSuccess': True, 'data': structured_data}

    @catching_errors()
    def select_recent_messages(self, chat_id: int, id_last_mes: int = None, quantity: int = 60) -> dict:
        """
        Возвращает последние сообщения из чата.

        :param chat_id: Id чата, сообщения которого будут возвращены.
        :param id_last_mes: Id последнего сообщения, которое вернётся. Если None, используется максимальный id в чате.
        :param quantity: Количество сообщений для возврата. По умолчанию 60
        :return: Словарь, где isSuccess = True, если ошибок нет, data = список словарей с инфо об сообщениях,
        иначе isSuccess = False, error = короткая ошибка, long_error = весь traceback
        В data храниться список словарей с инфо об пользователях
        """

        if id_last_mes is None:
            # Операция быстрая за счёт получение значения встроенного счётчика
            seq_request = f"SELECT last_value FROM mes_seq_{chat_id}"
            id_last_mes = self.session.execute(text(seq_request)).fetchone()[0]

        query = select(Messages).where(Messages.chat_id == chat_id,
                                            Messages.id > id_last_mes-quantity,
                                            Messages.id <= id_last_mes)
        raw_data = self.session.execute(query).scalars().all()
        structured_data = self._get_dict(raw_data)
        return {'isSuccess': True, 'data': structured_data}