# Инициализация классов таблиц и классов с методами
from Database.methods.configuring_classes import (UsersQueries, ChatsQueries,
                                                         ParticipantsQueries, MessagesQueries, FriendsQueries)
from Database.methods.init import Users, Chats, Participants, Messages, Friends
from Database.methods.basic_methods import BasicMethods
from Database.init import catching_errors
from sqlalchemy import select, func, desc

# Главный класс - через него осуществляется работа с методами
class DataBase(BasicMethods):
    def __init__(self, session):
        super().__init__(session)

        self.users = UsersQueries(session)
        self.chats = ChatsQueries(session)
        self.participants = ParticipantsQueries(session)
        self.messages = MessagesQueries(session)
        self.friends = FriendsQueries(session)

    def commit(self):
        """Удобная обёртка"""
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    @catching_errors()
    def select_all_users_by_chat_id(self, chat_id: int):
        """
        Получение всех пользователей, состоящих в чате

        :param chat_id: id чата, участников которого нужно вывести
        :return: isSuccess, где в data сохранён список словарей с полной инфой о пользователях
        """

        query = select(Users.__table__).join(Users.participants).where(Participants.chat_id == chat_id)
        data = self.session.execute(query).mappings().all()
        return [dict(row) for row in data]

    @catching_errors()
    def select_user_by_username(self, username: str) -> dict:
        """
        Вывод всей инфы о пользователе, через username

        :param username: username пользователя, которого нужно вывести
        :return: isSuccess, где в data сохранён словарь о всех данных пользователя
        """
        query = select(Users.__table__).where(Users.username == username)
        data = self.session.execute(query).mappings().one()
        return dict(data)

    @catching_errors()
    def select_user_by_id(self, id: int) -> dict:
        """
        Вывод всей инфы о пользователе, через id

        :param id: id пользователя, которого нужно вывести
        :return: isSuccess, где в data сохранён словарь о всех данных пользователя
        """
        query = select(Users.__table__).where(Users.id == id)
        data = self.session.execute(query).mappings().one()
        return dict(data)

    @catching_errors()
    def select_all_chats_by_id_user(self, user_id: int):
        """
        Получение всех чатов, в которых состоит пользователь

        :param user_id: id пользователя, список чатов которого нужно выдать
        :return: isSuccess, где в data сохранён список словарей с полной инфой о чатах пользовател
        """

        query = select(Chats.__table__).join(Chats.participants).where(Participants.user_id == user_id)
        data = self.session.execute(query).mappings().all()
        return [dict(row) for row in data]
    
    @catching_errors()
    def select_user_by_chat_id(self, chat_id: int, your_user_id: int) -> dict:
        """
        Получение следующей инфы о пользователе, состоящем в личной переписке:
        `id`, `name`, `username`, `lastname`, `birthday`, `datе_created`, `avatar_url`, `last_time_online`, `phone`, `email`

        :param chat_id: id чата с `type == "private" -> True`, инфо участника которого нужно получить
        :param your_user_id: id участника переписки, которому нужно узнать о юзере (то есть не сам пользователь, данные которого нужно узнать)
        :return: isSuccess, где в data сохранён словарь с инфой о пользователе в личной переписке
        """
        query = (
            select(Users.id, Users.name, Users.username, Users.lastname, Users.birthday, Users.date_created,
                   Users.avatar_url, Users.last_time_online, Users.phone, Users.email)
            .join(Participants, Users.id == Participants.user_id)
            .where(Participants.chat_id == chat_id, Users.id != your_user_id)
        )
        data = self.session.execute(query).mappings().one()
        return dict(data)

    @catching_errors()
    def select_chats(self, user_id: int):
        """
        Вывод полной нужной инфы для вывода всех чатов пользователя

        :param user_id: id пользователя, для которого нужно вывести список его чатов
        :return: isSuccess, где в data сохранён список словарей содержащие: `id`, `type`, `name`, `avatar_url`, `last_user_id`, `last_user_name`, `last_mes`, `user_count`, `date_created` (если последние сообщение написано юзером, для которого выводятся данные, то в `last_user_name` будет `'Вы'`)

        """

        query = (
            select(
                Chats.id, Chats.name, Chats.avatar_url,Chats.type, Chats.user_count,
                Chats.last_sender_id, Chats.last_sender_name, Chats.last_mes, Chats.date_created
            )
            .join(Participants).where(Participants.user_id == user_id)
        )

        # Выполнение и маппинг в нужный формат
        rows = self.session.execute(query).mappings().all()
        chats_data = []

        for row in rows:
            # Логика last_user
            last_sender_name = row.last_sender_name
            if row.last_sender_id == user_id:
                last_sender_name = "Вы"

            chats_data.append({
                "id": row.id,
                "type": row.type,
                "name": row.name,
                "avatar_url": row.avatar_url,
                "last_user_id": row.last_sender_id,
                "last_user_name": last_sender_name,
                "last_mes": row.last_mes,
                "user_count": row.user_count,
                "date_created": row.date_created
            })

        return chats_data

    @catching_errors()
    def select_recent_messages(self, chat_id: int, id_last_mes: int = None, quantity: int = 100) -> list[dict]:
        """
        Вывод определённого количества определённых сообщений

        :param chat_id: id чата, в котором нужно вывести сообщения
        :param id_last_mes: id последнего сообщения, которое должно быть возвращено (последние сообщение имеет наибольший id). По умолчанию равен последнему id в чате
        :param quantity: число сообщений, которое будет возвращено. По умолчанию - 100
        :return: isSuccess, где в data сохранён список словарей про сообщения
        """

        # Нахождение максимального id в данном чате, если не указан id последнего сообщения
        if id_last_mes is None:
            max_id_query = select(func.max(Messages.id)).where(Messages.chat_id == chat_id)
            id_last_mes = self.session.execute(max_id_query).scalar()

        # Взятие нужных сообщений, сортировка от новых к старым, ограничивание по количеству
        query = (
            select(Messages.__table__)
            .where(Messages.chat_id == chat_id, Messages.id <= id_last_mes)
            .order_by(desc(Messages.id))
            .limit(quantity)
        )

        rows = self.session.execute(query).mappings().all()
        return [dict(row) for row in rows][::-1]

    @catching_errors()
    def select_chat_participants(self, chat_id: int) -> list[dict]:
        """
        Вывод информации о чате
        ВАЖНО: используется, только если `Chats.type == 'group' -> True`. Если `Chats.type == 'private' -> True`, то использовать `select_user_by_chat_id`

        :param chat_id: id чата, инфо о котором нужно вывести
        :return: isSuccess, где в data сохранён список словарей содержащий инфо об участниках для их отображения: `id`, `name`, `avatar_url`, `last_time_online`
        """
        query = (
            select(Users.id, Users.name, Users.avatar_url, Users.last_time_online)
            .join(Participants, Users.id == Participants.user_id)
            .where(Participants.chat_id == chat_id)
        )

        participants = self.session.execute(query).mappings().all()

        return [dict(participant) for participant in participants]
