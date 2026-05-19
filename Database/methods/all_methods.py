# Инициализация классов таблиц и классов с методами
from Database.methods.configuring_classes import (UsersQueries, ChatsQueries,
                                                  ParticipantsQueries, MessagesQueries, FriendsQueries)
from Database.methods.init import Users, Chats, Participants, Messages, Friends
from Database.methods.basic_methods import BasicMethods
from Database.init import catching_errors
from sqlalchemy import select, text, func, and_, case, desc

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
        Получение всех пользователей, которые состоят в чате с chat_id = chat_id

        :param chat_id: id чата
        :return: словарь, где isSuccess = True, если ошибок нет, иначе False.
        В data храниться список словарей с инфо об пользователях
        """

        query = select(Users.__table__).join(Users.participants).where(Participants.chat_id == chat_id)
        data = self.session.execute(query).mappings().all()
        return [dict(row) for row in data]

    @catching_errors()
    def select_user_by_username(self, username: str) -> dict:
        query = select(Users.__table__).where(Users.username == username)
        data = self.session.execute(query).mappings().one()
        return dict(data)

    @catching_errors()
    def select_user_by_id(self, id: int) -> dict:
        query = select(Users.__table__).where(Users.id == id)
        data = self.session.execute(query).mappings().one()
        return dict(data)

    @catching_errors()
    def select_all_chats_by_id_user(self, user_id: int):
        """
        Получение всех чатов, в которых состоит пользователь с id = user_id

        :param user_id: id нужного пользователя
        :return: Список словарей, где словарь - данные о чате
        """

        query = select(Chats.__table__).join(Chats.participants).where(Participants.user_id == user_id)
        data = self.session.execute(query).mappings().all()
        return [dict(row) for row in data]
    
    @catching_errors()
    def select_user_by_chat_id(self, chat_id: int, user_id: int):
        query = (
            select(Users.id, Users.name, Users.username, Users.lastname, Users.birthday, Users.date_created,
                   Users.avatar_url, Users.last_time_online, Users.phone, Users.email)
            .join(Participants, Users.id == Participants.user_id)
            .where(Participants.chat_id == chat_id, Users.id != user_id)
        )
        data = self.session.execute(query).mappings().one()
        return dict(data)

    # Новые методы:
    chats_info_ = {'isSuccess': True,
                  'data': [
                      {'id': 1,
                       'type': 'group',
                       'name': 'Разработка немыслимого',
                       'small_avatar_url': None,
                       'last_mes': 'Спам 5.2',
                       'last_user': 'Вы',  # Потому что я отправитель
                       'user_count': 3,
                       },
                      {'id': 2,
                       'type': 'private',
                       'name': 'ЮН',
                       'small_avatar_url': None,
                       'last_mes': 'Дельно, но хотелось...',  # 20 символов.strip() + "..."
                       'last_user': 'Юра',
                       'user_count': None  # т. к. это личная переписка
                       },
                      {'id': 2,
                       'type': 'private',
                       'name': 'НС',
                       'small_avatar_url': None,
                       'last_mes': 'Начните общение',
                       'last_user': None,
                       'user_count': None  # т. к. всегда 2 юзера
                       }
                  ]
                  }  # Сделано! По id пользователя выводит при успехе данные всех чатов для их отображения
    messages_info_ = {'isSuccess': True,
                     'data': [
                         {'id': 11,
                          'type': 'text',
                          'text': 'Спам',
                          'file_id': None,
                          'creation_date_time': '02-05-2026 18:05:27',
                          'user_id': 1,
                          'sender_name': 'Вы'
                          },
                         {'id': 12,
                          'type': 'text',
                          'text': 'Спам 3',
                          'file_id': None,
                          'creation_date_time': '02-05-2026 18:05:31',
                          'user': 'Юра',
                          'user_id': 3
                          },
                         {'id': 13,
                          '...': '...'},
                         {'id': 14,
                          '...': '...'},
                         {'id': 15,
                          'type': 'text',
                          'text': 'Спам 5.2',
                          'file_id': None,
                          'creation_date_time': '02-05-2026 18:05:52',
                          'user': 'Вы',
                          'user_id': 1
                          }
                     ]
                     }  # Выводит последние сообщения по id чата (добавить sender_name в messages)
    chat_info_with_participants_ = {'isSuccess': True,
                 'data': {'id': 11,
                          'name': 'Разработка немыслимого',
                          'avatar_url': None,
                          'date_created': '02-05-2026',
                          'users': [
                              {
                                  'id': 1,
                                  'name': 'Никита',
                                  'avatar_url': None,
                                  'last_time_online': '02-05-2026 18:05:27'
                              },
                              {
                                  'id': 2,
                                  'name': 'Юра',
                                  'avatar_url': None,
                                  'last_time_online': '02-05-2026 15:15:52'
                              },
                              {
                                  'id': 3,
                                  'name': 'Сева',
                                  'avatar_url': None,
                                  'last_time_online': '02-05-2026 11:11:11'
                              }
                          ]
                          }
                 }  # Выводит инфо об чате и его пользователях по id чата

    @catching_errors()
    def select_chats(self, user_id: int):

        query = (
            select(
                Chats.id, Chats.name, Chats.avatar_url,Chats.type, Chats.user_count,
                Chats.last_sender_id, Chats.last_sender_name, Chats.last_mes
            )
            .join(Participants).where(Participants.user_id == user_id)
        )

        # Выполнение и маппинг в нужный формат
        rows = self.session.execute(query).mappings().all()
        chats_data = []

        for row in rows:
            # 👤 Логика last_user
            last_sender_name = row.last_sender_name
            if row.last_sender_id == user_id:
                last_sender_name = "Вы"

            chats_data.append({
                "id": row.id,
                "type": row.type,
                "name": row.name,
                "small_avatar_url": row.avatar_url,
                "last_user_id": row.last_sender_id,
                "last_user_name": last_sender_name,
                "last_mes": row.last_mes,
                "user_count": row.user_count,
            })

        return chats_data

    @catching_errors()
    def select_recent_messages(self, chat_id: int, id_last_mes: int = None, quantity: int = 100):
        """
        Возвращает последние сообщения из чата.

        :param chat_id: Id чата, сообщения которого будут возвращены.
        :param id_last_mes: Id последнего сообщения, которое вернётся. Если None, используется максимальный id в чате.
        :param quantity: Количество сообщений для возврата. По умолчанию 60
        :return: Словарь, где isSuccess = True, если ошибок нет, data = список словарей с инфо об сообщениях,
        иначе isSuccess = False, error = короткая ошибка, long_error = весь traceback
        В data храниться список словарей с инфо об пользователях
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
    def select_chat_info(self, chat_id: int) -> list | dict:
        """
        Для вызова только если нужно узнать инфо группы (type = 'group')
        """
        query_chat = select(Chats.id, Chats.name, Chats.avatar_url, Chats.date_created).where(Chats.id==chat_id)
        query = (
            select(Users.id, Users.name, Users.avatar_url, Users.last_time_online)
            .join(Participants, Users.id == Participants.user_id)
            .where(Participants.chat_id == chat_id)
        )

        chat_info = dict(self.session.execute(query_chat).mappings().one())
        participants = self.session.execute(query).mappings().all()

        chat_info['participants'] = [user for user in participants]
        return chat_info