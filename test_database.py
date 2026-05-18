"""
Файл основного кода
"""

from Database.api import Session, DataBase

def health_check_users(db):
    def views():
        print('-' * 150)

        users = db.users.select_all()
        if users['isSuccess']:
            for user in users['data']:
                # print(user['id'], user['name'], user['username'])
                print(user)

        # else:
            # print(users['error'])
            # print(users['long_error'])

        print('-' * 150)

    views()

    # users = db.users.select_all_users_by_chat_id(chat_id=2)
    # if users['isSuccess']:
    #     for user in users['data']:
    #         print(user['id'], user['name'], user['username'])

    # print(db.users.exists(username='Nikita'))  # >>> True
    # print(db.users.exists(username='Nikitka')) # >>> False
    # print(db.users.exists(username='Yura3'))  # >>> False
    # print(db.users.exists(username='Seva2'))   # >>> False
    # print(db.users.exists(username='Seva'))    # >>> True
    # print(db.users.exists(username='Yura'))    # >>> True

    # if not db.users.exists(username='Nikita'):
    #     print(db.users.add(name='Никита', username='Nikita', lastname='Соколов',
    #              birthday='12-01-2011', phone='89012345678', email='mail@yandex.ru', password='Nik'))
    # print(db.users.add(name='Сева', username='Seva', lastname=None, birthday=None, phone='89876543210', email=None,
    #                    password='Sev'))
    # print(db.users.add(name='Юра', username='Yura', lastname='Мельник', birthday='14-07-2011', phone=None, email=None,
    #                    password='Yur'))
    # print(db.users.add(name='123', username='123', lastname='123-123', birthday=None, phone=None, email=None,
    #                    password='123'))

    # print(db.users.update(1, 'password', 'Nik'))
    # print(db.users.update(9, 'id', 2))
    # print(db.users.update(10, 'id', 3))
    # print(db.users.update(11, 'id', 4))
    # views()

    # isRealId = db.users.exists(id=17)
    # if isRealId:
    #     print(db.users.delete(17))
    views()

def health_check_chats(db):

    def views():
        print('-' * 150)

        chats = db.chats.select_all()
        if chats['isSuccess']:
            for chat in chats['data']:
                # print(chat['id'], chat['name'])
                print(chat)

        print('-' * 150)

    views()

    # print(f'Чаты пользователя с id= 1')
    # chats = db.chats.select_all_chats_by_id_user(user_id=1)
    # if chats['isSuccess']:
    #     for chat in chats['data']:
    #         print(chat)
    #
    # print('-' * 150)

    # db.chats.add(name='Разработка немыслимого')
    # db.chats.add(name='ЮН')
    # db.chats.add(name='НС')
    # db.chats.add(name='СЮ')
    # print(db.chats.add(name='СЮh'))
    # views()

    # print(db.chats.update(16, 'id', 1))
    # print(db.chats.update(7, 'id', 2))
    # print(db.chats.update(8, 'id', 3))
    # print(db.chats.update(1, 'avatar_url', 4123456))
    # views()

    # db.chats.delete(1)
    # views()

def health_check_participants(db):
    def views():
        print('-' * 150)
        participants = db.participants.select_all()
        if participants['isSuccess']:
           for participant in participants['data']:
                # print(f'chat_id: {participant['chat_id']}, user_id: {participant["user_id"]}')
                print(participant)

        print('-' * 150)

    views()

    # db.participants.add(chat_id=1, user_id=1)
    # db.participants.add(chat_id=1, user_id=2)
    # db.participants.add(chat_id=1, user_id=3)
    #
    # db.participants.add(chat_id=2, user_id=1)
    # db.participants.add(chat_id=2, user_id=3)
    #
    # db.participants.add(chat_id=3, user_id=1)
    # db.participants.add(chat_id=3, user_id=2)
    #
    # db.participants.add(chat_id=4, user_id=1)
    # db.participants.add(chat_id=4, user_id=2)
    # db.participants.add(chat_id=4, user_id=3)
    # print(db.participants.add(chat_id=4, user_id=5))

    # print(db.participants.update(chat_id=1, user_id=1, attr_name='role', value='Админ'))
    # views()

    # print(db.participants.delete(user_id=1 , chat_id=4))
    # views()

def health_check_messages(db):
    def views():
        print('-' * 150)
        messages = db.messages.select_all()
        if messages['isSuccess']:
            for message in messages['data']:
               print(message)

        print('-' * 150)

    views()

    # messages = db.messages.select_all_messages_by_chat_id(chat_id=4)
    # if messages['isSuccess']:
    #     for message in messages['data']:
    #         print(message)


    # db.messages.add(chat_id=1, user_id=1, mes_mes_text='Привет всем от Никиты!')
    # db.messages.add(chat_id=1, user_id=2, mes_text='Привет всем от Севы!')
    # db.messages.add(chat_id=1, user_id=3, mes_text='Привет всем от Юры!')
    # db.messages.add(chat_id=2, user_id=3, mes_text='Никит, как дела? (от Юры)')
    # db.messages.add(chat_id=4, user_id=2, mes_text='Юр, как дела? (от Севы)')
    # db.messages.add(chat_id=1, user_id=2, mes_text='Как удалить это сообщение?')
    # db.messages.add(chat_id=1, user_id=1, mes_text='Как вам моя БД?')
    # db.messages.add(chat_id=1, user_id=1, mes_text='Спам')
    # db.messages.add(chat_id=1, user_id=1, mes_text='Спам')
    # db.messages.add(chat_id=1, user_id=2, mes_text='Спам 1')
    # db.messages.add(chat_id=1, user_id=2, mes_text='Спам')
    # db.messages.add(chat_id=1, user_id=2, mes_text='Спам 2')
    # db.messages.add(chat_id=1, user_id=3, mes_text='Спам')
    # db.messages.add(chat_id=1, user_id=3, mes_text='Спам 3')
    # db.messages.add(chat_id=1, user_id=3, mes_text='Спам')
    # db.messages.add(chat_id=1, user_id=1, mes_text='Спам 4')
    # db.messages.add(chat_id=1, user_id=1, mes_text='Спам 5.2')
    # db.messages.add(chat_id=2, user_id=1, mes_text="Дельно")
    # views()
    #
    # db.messages.update(21, 'text', '嗨 everyone!')
    # views()
    #
    # db.messages.delete(20)
    # views()

def health_check_friends(db):
    def views():
        print('-' * 150)

        friends = db.friends.select_all()
        if friends['isSuccess']:
            for friend in friends['data']:
                print(friend)
        else:
            print(friends['error'])
            print(friends['long_error'])

        print('-' * 150)

    views()

    # print(db.friends.add(user_id_1=1, user_id_2=2, level_relationships=4))
    # print(db.friends.add(user_id_1=1, user_id_2=3, level_relationships=2))
    # print(db.friends.add(user_id_1=1, user_id_2=4, level_relationships=1))

    # print(db.friends.add(user_id_1=3, user_id_2=4, level_relationships=3))
    # views()

    # print(db.friends.update(id=[1, 2], attr_name="level_relationships", value=4))
    # views()

    # print(db.friends.delete(user_id_1=4, user_id_2=3))
    # views()

def test_real_simulated(db):
    """
    Проверка работоспособности кода.
    Ты, надеюсь сможешь переделать это в рабочий интерфейс
    """


    sing = input('1- зарегистрироваться\n2 - войти\nНомер действия: ')
    if sing == '1':
        username = input('Придумайте свой username: ')
        # Пока username существует
        while db.users.exists(username=username):
            print('Такой username уже занят. Попробуйте другой')
            username = input('username: ')

        name = input('Придумайте свой Ник: ')
        password = input('Придумайте свой пароль: ')

        # Добавление пользователя в БД
        response = db.users.add(name=name, username=username, password=password)
        if response['isSuccess']:
            print('Вы успешно зарегистрировались')

            # Вывод всех пользователй
            users = db.users.select_all()
            if users['isSuccess']:
                print('Список всех пользователей:')
                for user in users['data']:
                    print(user['name'], user['username'])

            else:
                print('Если вы видите это, значит знайте: это ошибка.')
                print(users)

        else:
            print('Если вы видите это, значит знайте: это ошибка')
            print(response)


    elif sing == '2':
        username = input('Введите свой username: ')
        password = input('Введите свой пароль: ')

        # Пока username и password не будут относиться к одной строчке
        isAble = db.users.exists(username=username, password=password)
        while not isAble:
            print('Неправильный username или пароль')
            username = input('username: ')
            password = input('пароль: ')
            isAble = db.users.exists(username=username, password=password)

        # Получение словаря в user_response['data'], где есть id и name
        user_response = db.select_id_name_by_username(username=username)
        if user_response['isSuccess']:
            user = user_response['data']
            print(f'Жалуйте добро, {user['name']}')

            # Получение всех чатов, которые есть у пользователя (вся инфа об чате, подробнее см. в models/chats.py)
            chats = db.select_all_chats_by_id_user(user_id=user['id'])
            if chats['isSuccess']:
                print('Выберите чат из списка доступных:', end=' ')
                for chat in chats['data']:
                    print(chat['name'], end=', ')

                selected_chat = input('\nЧат: ')
                for chat in chats['data']:
                    if chat['name'] == selected_chat:
                        chat_id = chat['id']
                        break

                # Получение всех сообщений, которые есть в чате (вся инфа об сообщении, подробнее см. в models/messages.py)
                messages = db.select_all_messages_by_chat_id(chat_id=chat_id)
                if messages['isSuccess']:
                    for message in messages['data']:
                        # Получение имени пользователя по id
                        name_response = db.select_user_name_by_id(message['user_id'])
                        if name_response['isSuccess']:
                            print(f'[{name_response['data']['name']}]: {message['text']}')
                        else:
                            print('Если вы видите это, значит знайте: это ошибка')
                            print(name_response)

                else:
                    print('Если вы видите это, значит знайте: это ошибка')
                    print(chats)

            else:
                print('Если вы видите это, значит знайте: это ошибка.')
                print(chats)

        else:
            print('Если вы видите это, значит знайте: это ошибка')
            print(user_response)


    # print('Выберите чат из доступных:')
    # print(f'[{'user'}]: {'message'}')

def get_all_data(db) -> dict:
    users = db.users.select_all()
    chats = db.chats.select_all()
    messages = db.messages.select_all()
    participants = db.participants.select_all()
    friends = db.friends.select_all()
    all_data = {'users': users['data'],
                'chats': chats['data'],
                'participants': participants['data'],
                'messages': messages['data'],
                'friends': friends['data']}
    print(all_data)
    return all_data

def set_backup(db, all_data: dict):
    for model, list_data in all_data.items():
        for data in list_data:
            table = getattr(db, model)
            # print(data)
            print(table.add(**data))
            # print(f'db.{model}.add({data})')

# Создание сессии
with Session() as session:
    db = DataBase(session)
    # РАБОЧАЯ ЧАСТЬ
    # print(db.users.exists(username='Nikita'))
    # print(db.select_user_by_username('Nikita'))
    health_check_users(db)  # Посмотреть всех пользователей
    health_check_chats(db)  # Посмотреть чаты
    health_check_participants(db)  # Участники групп
    health_check_messages(db)  # Сообщения
    health_check_friends(db)
    exit()
    # test_real_simulated(db)  # Симуляция регистрации или авторизации

    # бэкап всех тестовых данных для быстрого восстановления
    backup = {
            'users': [
                {'avatar_url': None, 'birthday': '12-01-2011', 'date_created': '01-05-2026',
                 'email': 'mail@yandex.ru', 'id': 1, 'lastname': 'Соколов', 'name': 'Никита', 'password': 'Nik',
                 'phone': '89012345678', 'username': 'Nikita'},
                {'avatar_url': None, 'birthday': None, 'date_created': '01-05-2026', 'email': None, 'id': 2,
                 'lastname': None, 'name': 'Сева', 'password': 'Sev', 'phone': '89876543210', 'username': 'Seva'},
                {'avatar_url': None, 'birthday': '14-07-2011', 'date_created': '01-05-2026', 'email': None, 'id': 3,
                 'lastname': 'Мельник', 'name': 'Юра', 'password': 'Yur', 'phone': None, 'username': 'Yura'},
                {'avatar_url': None, 'birthday': None, 'date_created': '01-05-2026', 'email': None, 'id': 4,
                 'lastname': None, 'name': '123', 'password': '1111', 'phone': None, 'username': '123'},
                {'avatar_url': None, 'birthday': None, 'date_created': '02-05-2026', 'email': None, 'id': 5,
                 'lastname': None, 'name': '1234444', 'password': '1111', 'phone': None, 'username': '12344444444'},
                {'avatar_url': None, 'birthday': None, 'date_created': '02-05-2026', 'email': None, 'id': 8,
                 'lastname': None, 'name': '1234444', 'password': '1111', 'phone': None, 'username': '1234444444s4'}
            ],
            'chats': [
                {'avatar_url': None, 'date_created': '01-05-2026', 'id': 1, 'name': 'Разработка немыслимого',
                 'type': 'private'},
                {'avatar_url': None, 'date_created': '01-05-2026', 'id': 2, 'name': 'ЮН', 'type': 'private'},
                {'avatar_url': None, 'date_created': '01-05-2026', 'id': 3, 'name': 'НС', 'type': 'private'},
                {'avatar_url': None, 'date_created': '01-05-2026', 'id': 4, 'name': 'СЮ', 'type': 'private'},
                {'avatar_url': None, 'date_created': '01-05-2026', 'id': 5, 'name': 'СЮ', 'type': 'private'},
                {'avatar_url': None, 'date_created': '02-05-2026', 'id': 11, 'name': 'СЮh', 'type': 'private'},
                {'avatar_url': None, 'date_created': '02-05-2026', 'id': 6, 'name': 'СЮh', 'type': 'private'}
            ],
            'participants': [
                {'chat_id': 1, 'role': 'Участник', 'user_id': 1},
                {'chat_id': 1, 'role': 'Участник', 'user_id': 2},
                {'chat_id': 1, 'role': 'Участник', 'user_id': 3},
                {'chat_id': 2, 'role': 'Участник', 'user_id': 1},
                {'chat_id': 2, 'role': 'Участник', 'user_id': 3},
                {'chat_id': 3, 'role': 'Участник', 'user_id': 1},
                {'chat_id': 3, 'role': 'Участник', 'user_id': 2},
                {'chat_id': 4, 'role': 'Участник', 'user_id': 1},
                {'chat_id': 4, 'role': 'Участник', 'user_id': 2},
                {'chat_id': 4, 'role': 'Участник', 'user_id': 3},
                {'chat_id': 4, 'role': 'Участник', 'user_id': 5}
            ],
            'messages': [
                {'chat_id': 1, 'file_id': None, 'id': 1, 'text': 'Привет всем от Никиты!', 'type': 'text',
                 'user_id': 1},
                {'chat_id': 1, 'file_id': None, 'id': 2, 'text': 'Привет всем от Севы!', 'type': 'text',
                 'user_id': 2},
                {'chat_id': 1, 'file_id': None, 'id': 3, 'text': 'Привет всем от Юры!', 'type': 'text',
                 'user_id': 3},
                {'chat_id': 2, 'file_id': None, 'id': 1, 'text': 'Никит, как дела? (от Юры)', 'type': 'text',
                 'user_id': 3},
                {'chat_id': 4, 'file_id': None, 'id': 1, 'text': 'Юр, как дела? (от Севы)', 'type': 'text',
                 'user_id': 2},
                {'chat_id': 1, 'file_id': None, 'id': 4, 'text': 'Как удалить это сообщение?', 'type': 'text',
                 'user_id': 2},
                {'chat_id': 1, 'file_id': None, 'id': 5, 'text': 'Как вам моя БД?', 'type': 'text', 'user_id': 1},
                {'chat_id': 1, 'file_id': None, 'id': 6, 'text': 'Спам', 'type': 'text', 'user_id': 1},
                {'chat_id': 1, 'file_id': None, 'id': 7, 'text': 'Спам', 'type': 'text', 'user_id': 1},
                {'chat_id': 1, 'file_id': None, 'id': 8, 'text': 'Спам 1', 'type': 'text', 'user_id': 2},
                {'chat_id': 1, 'file_id': None, 'id': 9, 'text': 'Спам', 'type': 'text', 'user_id': 2},
                {'chat_id': 1, 'file_id': None, 'id': 10, 'text': 'Спам 2', 'type': 'text', 'user_id': 2},
                {'chat_id': 1, 'file_id': None, 'id': 11, 'text': 'Спам', 'type': 'text', 'user_id': 3},
                {'chat_id': 1, 'file_id': None, 'id': 12, 'text': 'Спам 3', 'type': 'text', 'user_id': 3},
                {'chat_id': 1, 'file_id': None, 'id': 13, 'text': 'Спам', 'type': 'text', 'user_id': 3},
                {'chat_id': 1, 'file_id': None, 'id': 14, 'text': 'Спам 4', 'type': 'text', 'user_id': 1},
                {'chat_id': 2, 'file_id': None, 'id': 2, 'text': 'Дельно', 'type': 'text', 'user_id': 1},
                {'chat_id': 1, 'file_id': None, 'id': 15, 'text': 'Спам 5.2', 'type': 'text', 'user_id': 1}
            ],
            'friends': [
                {'level_relationships': 2, 'user_id_1': 1, 'user_id_2': 3},
                {'level_relationships': 1, 'user_id_1': 1, 'user_id_2': 4},
                {'level_relationships': 3, 'user_id_1': 2, 'user_id_2': 3},
                {'level_relationships': 4, 'user_id_1': 1, 'user_id_2': 2}
            ]
        }
    # backup = get_all_data(db) # создание бэкапа
    # set_backup(db, backup)  # восстановление бэкапа


