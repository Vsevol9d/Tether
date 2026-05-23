"""
Код для теста БД
"""

# Так будут формироваться названия для файлов (текущее время в миллисекундах + "_" + набор из 8 символов)
# import time, secrets
#
# def generate_unique_filename(extension: str = 'svg') -> str:
#     timestamp_ms = int(time.time() * 1000)
#     suffix = secrets.token_hex(4)  # 8 символов, например 'a3f5c2b1'
#     return f"{timestamp_ms}_{suffix}.{extension.lstrip('.')}"
#
# print(generate_unique_filename())

from Database.api import Session, DataBase

users_data = [
        {'name': 'Никита', 'username': 'Nikita', 'lastname': 'Соколов', 'birthday': '12-01-2011',
         'phone': '89012345678', 'email': 'mail@yandex.ru', 'password': 'Nik'},
        {'name': 'Сева', 'username': 'Seva', 'lastname': None, 'birthday': None, 'phone': '89876543210', 'email': None,
         'password': 'Sev'},
        {'name': 'Юра', 'username': 'Yura', 'lastname': 'Мельник', 'birthday': '14-07-2011', 'phone': None,
         'email': None, 'password': 'Yur'},
        {'name': '123', 'username': '123', 'lastname': '123-123', 'birthday': None, 'phone': None, 'email': None,
         'password': '123'},

        {'name': '', 'username': 'System', 'password': 'Tether_sys0'}
    ]
chats_data = [
        {'name': 'Разработка немыслимого', 'type': 'group'},
        {'name': 'ЮН', 'type': 'private'},
        {'name': 'НС'},
        {'name': 'СЮ'},
        {'name': 'Группа по группам', 'type': 'group'}
    ]
participants_data = [
        # Чат 1: Разработка немыслимого (Users: 1, 2, 3)
        {'chat_id': 1, 'user_id': 1},
        {'chat_id': 1, 'user_id': 2},
        {'chat_id': 1, 'user_id': 3},

        # Чат 2: ЮН (Users: 1, 3)
        {'chat_id': 2, 'user_id': 1},
        {'chat_id': 2, 'user_id': 3},

        # Чат 3: НС (Users: 1, 2)
        {'chat_id': 3, 'user_id': 1},
        {'chat_id': 3, 'user_id': 2},

        # Чат 4: СЮ (Users: 2, 3)
        {'chat_id': 4, 'user_id': 2},
        {'chat_id': 4, 'user_id': 3},
    ]
messages_data = [
        # Чат 1
        {'chat_id': 1, 'user_id': 1, 'text': 'Привет всем от Никиты!'},
        {'chat_id': 1, 'user_id': 2, 'text': 'Привет всем от Севы!'},
        {'chat_id': 1, 'user_id': 3, 'text': 'Привет всем от Юры!'},
        {'chat_id': 1, 'user_id': 2, 'text': 'Как удалить это сообщение?'},
        {'chat_id': 1, 'user_id': 1, 'text': 'Как вам моя БД?'},
        {'chat_id': 1, 'user_id': 1, 'text': 'Спам'},
        {'chat_id': 1, 'user_id': 1, 'text': 'Спам'},
        {'chat_id': 1, 'user_id': 2, 'text': 'Спам 1'},
        {'chat_id': 1, 'user_id': 2, 'text': 'Спам'},
        {'chat_id': 1, 'user_id': 2, 'text': 'Спам 2'},
        {'chat_id': 1, 'user_id': 3, 'text': 'Спам'},
        {'chat_id': 1, 'user_id': 3, 'text': 'Спам 3'},
        {'chat_id': 1, 'user_id': 3, 'text': 'Спам'},
        {'chat_id': 1, 'user_id': 1, 'text': 'Спам 4'},
        {'chat_id': 1, 'user_id': 1, 'text': 'Спам 5.2'},

        # Чат 3
        {'chat_id': 3, 'user_id': 2, 'text': 'Никит, как дела? (от Севы)'},

        # Чат 4
        {'chat_id': 4, 'user_id': 2, 'text': 'Сев, как дела? (от Юры)'},
        {'chat_id': 4, 'user_id': 1, 'text': "Дельно"},
        {'chat_id': 4, 'user_id': 2, 'text': "У меня тож дельно"},
    ]
friends_data = [
    {'user_id_1': 1, 'user_id_2': 2, 'level_relationships': 4},
    {'user_id_1': 1, 'user_id_2': 3, 'level_relationships': 2},
    {'user_id_1': 1, 'user_id_2': 4, 'level_relationships': 1},
]

def view_result_func(res, dash=True):
    # Вывод данных формата isSuccess
    if dash: print('-' * 150)
    if res['isSuccess']:
        if type(res['data']) != dict:
            for data in res['data']:
                print(data)
        else:
            print(res['data'])
    else:
        print('error:', res['error'])
        print('long_error:', res['long_error'])

def view(model):
    # Вывод всех данных из выбранной таблицы
    datas = getattr(db, model)
    dict = datas.select_all()
    view_result_func(dict)

    if dict['isSuccess']: return dict['data']
    return None  # или dict

def view_all():
    # Вывод всех данных и возврат их в виде словаря списков словарей
    all_data = dict()
    for model in ['users', 'chats', 'participants', 'messages', 'friends']:
        data_model = view(model)
        all_data[model] = data_model

    return all_data


def health_check_users(model='users'):
    # view_result_func(db.users.add_many(*users_data))
    # db.users.update(5, 'id', 0)
    # view(model)
    view_result_func(db.users.update(1, avatar_url='1779523841751_f9d7eb42'))
    view(model)

def health_check_chats(model='chats'):
    #view(model)
    # view_result_func(db.chats.add_many(*chats_data))
    # view_result_func(db.chats.add('Чат с тестом'))
    # view_result_func(db.chats.delete(7))
    view(model)

def health_check_participants(model='participants'):
    # view_result_func(db.participants.add_many(*participants_data))
    # view_result_func(db.participants.add(chat_id=1, user_id=4))
    # view_result_func(db.participants.delete(chat_id=1, user_id=4))
    view(model)
    # view_result_func(db.participants.add_many({'chat_id': 5, 'user_id': 1}, {'chat_id': 5, 'user_id': 4}))

def health_check_messages(model='messages'):
    # view_result_func(db.messages.add_many(*messages_data))
    # view_result_func(db.messages.delete(24))
    view(model)
    # view_result_func(db.messages.add(chat_id=5, user_id=4, sender_name='123', text='Кто я и зачем я существую?'))

def health_check_friends(model='friends'):
    # view_result_func(db.friends.add_many(*friends_data))
    # db.friends.delete(2, 1)
    view(model)
    # view_result_func(db.friends.update(user_id_1=3, user_id_2=1, level_relationships=2))
    # view(model)

def test_navigation(user_id):
    """
    Пример без UI по получению списка чатов, сообщений в чате, инфы о чате
    """
    print('Доступные вам чаты (нужно подождать):')
    chats = db.select_chats(user_id=user_id)
    view_result_func(chats, False)
    chat_id = int(input('Введите id чата, в который хотите зайти: '))
    current_chat = dict()
    for chat in chats['data']:
        if chat['id'] == chat_id:
            current_chat = chat

    print('\nПоследние 5 сообщений в чате:')
    messages = db.select_recent_messages(chat_id=chat_id, quantity=5)
    view_result_func(messages, False)

    print('\nИнфо о чате (или пользователе, если это личная переписка):')
    if current_chat['type'] == 'private':
        user_info = db.select_user_by_chat_id(chat_id=3, user_id=1)
        view_result_func(user_info, False)
    elif current_chat['type'] == 'group':
        chat_info = db.select_chat_info(chat_id=chat_id)
        view_result_func(chat_info, False)
        print('Участники:')
        for participant in chat_info['data']['participants']:
            print(participant)

# Создание экземпляра класса с определённой сессией
db = DataBase(Session())
# view_all()

# обновление и удаление полей Messages.sender_name, Chats: user_count, last_sender_id, last_sender_name, last_mes
# если пользователь обновлён или удалён

health_check_users()  # Посмотреть всех пользователей
# health_check_chats()  # Посмотреть чаты
# health_check_participants()  # Участники групп
# health_check_messages()  # Сообщения
# health_check_friends() # Друзья

# test_navigation(user_id=1)  # Пример получения данных