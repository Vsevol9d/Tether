"""
Этот файл нужен для создания подсказок при вызове основных функций
"""
from Database.init import catching_errors
from Database.methods.basic_methods import BasicMethods
from Database.methods.init import Users, Chats, Participants, Messages, Friends
from Database.models.messages import allowed_types
from sqlalchemy.orm import Session
from typing import Literal
from sqlalchemy import update


class UsersQueries(BasicMethods[Users]):
    __AttrName = Literal["name", "username", "lastname", "birthday", "avatar_url",
    "last_time_online", "password", "phone", "email"]

    def __init__(self, session: Session):
        super().__init__(session, Users)

    # Чтобы были подсказки
    @catching_errors(commit=True)
    def add(self, name: str, username: str, password: str, lastname: str = None, birthday: str = None,
            avatar_url: str = None, phone: str | int = None, email: str = None, last_time_online: str = None) -> dict:

        return super()._add(name=name, username=username, lastname=lastname, last_time_online=last_time_online,
                           birthday=birthday, avatar_url=avatar_url, phone=phone, email=email, password=password)

    # def update(self, pk: int | list) -> dict:
    #     return super().update(pk=pk, **kwargs)


class ChatsQueries(BasicMethods[Chats]):
    def __init__(self, session: Session):
        super().__init__(session, Chats)  # Инициализация базовых четырёх методов

    @catching_errors(commit=True)
    def add(self, name: str, avatar_url: str = None, type: str = None) -> dict:
        # Получение следующего id чата
        chat_info = super()._add(name=name, avatar_url=avatar_url, type=type, last_mes='Чат создан',
                                 last_sender_name='', last_sender_id=0)

        sys_msg = Messages(chat_id=chat_info['id'], user_id=0, type='text', text='Чат создан')
        self.session.add(sys_msg)

        return chat_info

    @catching_errors(commit=True)
    def add_many(self, *args) -> list:
        # Массовое создание чатов
        # chats_data = super()._add_many(*args)
        return [self.add(**row) for row in args]
        # Не используется создание системных сообщений, так как add_many для chats нужен только для бэкапов,
        # где эти системные сообщения и так существуют и имеют определённый id
        '''
        # Формирование системных сообщений для каждого созданного чата
        sys_msgs = [Messages(chat_id=c['id'], user_id=0, type='text', text='Чат создан') for c in chats_data]
        if sys_msgs:
            self.session.add_all(sys_msgs)
        '''

        return chats_data



class ParticipantsQueries(BasicMethods[Participants]):
    def __init__(self, session: Session):
        super().__init__(session, Participants)

    @catching_errors(commit=True)
    def add(self, chat_id: int, user_id: int, role: str = None) -> dict:
        stmt = update(Chats).where(Chats.id == chat_id).values(user_count=Chats.user_count + 1)
        self.session.execute(stmt)
        return super()._add(chat_id=chat_id, user_id=user_id, role=role)

    @catching_errors(commit=True)
    def update(self, chat_id: int, user_id: int, **kwargs) -> dict:
        return super()._update(pk=[chat_id, user_id], **kwargs)

    @catching_errors(commit=True)
    def delete(self, chat_id: int, user_id: int) -> dict:
        return super()._delete((chat_id, user_id))

    @catching_errors(commit=True)
    def add_many(self, *args) -> list:
        """
        Массовое добавление участников с автоматическим инкрементом Chats.user_count
        """
        # many_data = super()._add_many(*args)
        return [self.add(**row) for row in args]

        # Подсчёт: сколько участников добавлено в каждый chat_id
        chat_increments = {}
        items = args[0] if len(args) == 1 and isinstance(args[0], list) else args  # распаковка args
        for data in items:
            cid = data.get('chat_id')
            chat_increments[cid] = chat_increments.get(cid, 0) + 1

        # Обновление счётчиков (один UPDATE на каждый уникальный чат)
        for cid, count in chat_increments.items():
            stmt = update(Chats).where(Chats.id == cid).values(user_count=Chats.user_count + count)
            self.session.execute(stmt)

        return many_data


class MessagesQueries(BasicMethods[Messages]):
    def __init__(self, session: Session):
        super().__init__(session, Messages)

    @catching_errors(commit=True)
    def add(self, chat_id: int, user_id: int, sender_name: int,
            type: str = 'text', text: str = None, file_id: int = None) -> dict:
        """
        Специальный add для сообщений.
        Получает локальный id = nextval(mes_seq_<chat_id>) и вставляет запись.
        """
        msg_data = {"chat_id": chat_id, "user_id": user_id, "type": type, "text": text, "file_id": file_id,
                    "sender_name": sender_name}

        self.session.add(Messages(**msg_data))
        self.session.flush()

        # Определение текста последнего сообщения, выводимое в список чатов
        # Обрезка до последних 20 символов, чтобы влезло в список чатов
        if type == 'text': last_mes = text[:20] + ('...' if len(text) > 20 else '')
        else: last_mes = allowed_types.get(type, "Неопределённое сообщение")

        # Обновление последнего сообщения и его отправителя
        stmt = update(Chats).where(Chats.id == chat_id).values(
            last_sender_name=sender_name, last_sender_id=user_id, last_mes=last_mes)
        self.session.execute(stmt)
        return msg_data

    @catching_errors(commit=True)
    def add_many(self, *args) -> list:
        # Массовая вставка сообщений
        return [self.add(**row) for row in args]
        result = super()._add_many(*args)

        # Группировка последних сообщений по chat_id
        chats_update = {}
        for data in args:
            chats_update[data['chat_id']] = data  # Перезаписывание, остаётся последнее

        # Обновление превью чатов
        for cid, data in chats_update.items():
            text = data.get('text')
            if data.get('type') == 'text': last_mes = text[:20] + ('...' if len(text) > 20 else '')
            else: last_mes = allowed_types.get(type, "Неопределённое сообщение")

            stmt = update(Chats).where(Chats.id == cid).values(
                last_sender_name=data.get('sender_name'), last_sender_id=data.get('user_id'), last_mes=last_mes)
            self.session.execute(stmt)

        return result

class FriendsQueries(BasicMethods[Friends]):
    def __init__(self, session: Session):
        super().__init__(session, Friends)

    @catching_errors(commit=True)
    def add(self, user_id_1: int, user_id_2: int, level_relationships: int = None) -> dict:
        if user_id_1 > user_id_2: user_id_1, user_id_2 = user_id_2, user_id_1
        return super()._add(user_id_1=user_id_1, user_id_2=user_id_2, level_relationships=level_relationships)

    @catching_errors(commit=True)
    def delete(self, user_id_1: int, user_id_2: int) -> dict:
        if user_id_1 > user_id_2: user_id_1, user_id_2 = user_id_2, user_id_1
        return super()._delete((user_id_1, user_id_2))

    @catching_errors(commit=True)
    def update(self, user_id_1: int, user_id_2: int, **kwargs) -> dict:
        if user_id_2 < user_id_1:
            user_id_1, user_id_2 = user_id_2, user_id_1
        return super()._update(pk=[user_id_1, user_id_2], **kwargs)

    @catching_errors(commit=True)
    def add_many(self, *args) -> list:
        return [self.add(**row) for row in args]
        # Предобработка: сортировка ID для составного PK
        items = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        for d in items:
            if d['user_id_1'] > d['user_id_2']:
                d['user_id_1'], d['user_id_2'] = d['user_id_2'], d['user_id_1']

        # Массовая вставка
        return super()._add_many(*args)