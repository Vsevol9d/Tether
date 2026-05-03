import customtkinter as ctk
import sys, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_AVATAR_PATH = BASE_DIR / "assets" / "default_avatar.jpg"

sys.path.append(os.path.abspath("../Database"))

from UI.pages.start_page import StartPage
from UI.pages.chatting_page import ChattingPage
from UI.pages.adding_page import AddingPage
from UI.pages.sign_up_page import SignUpPage
from UI.element_views.chat_view import MessageView, ChatView, ChatInfoView
from UI.element_views.selectable_chat_view import SelectableChatView
from Database.api import Session, DataBase

# Обработчик ошибок со стороны UI
from error_handler import ErrorHandler

with Session() as session:
    db = DataBase(session)

# Настройка внешнего вида (можно вынести в initialize)
ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("800x600")
        self.root.title("Tether")

        self.user = None
        self.available_chats = {}
        self.current_chat_view = None
        self.current_chat_info = None
        self.is_authorized = False
        self.addable_users_names = []
        self.addable_users = []

        # Инициализация классов страниц
        self.start_page = StartPage(self.root)
        self.sign_up_page = SignUpPage(self.root, self.register_user, self.login_user)

        self.current_page = self.start_page

        # Страницы для которых требуются данные из БД, инициализируются позже
        self.chatting_page = None
        self.adding_page = None

    def switch_to_chatting_page(self) -> None:
        if not self.is_authorized:
            # Получаем чаты по id пользователя
            chats = db.select_all_chats_by_id_user(user_id=self.user['id'])
            if chats['isSuccess']:
                for chat in chats['data']:
                    chat_id = chat['id']
                    chat_name = chat['name']
                    last_message = ''
                    participants_list = []
                    participants_names_list = []

                    participants_response = db.select_all_users_by_chat_id(chat_id=chat_id)
                    if participants_response['isSuccess']:
                        for user in participants_response['data']:
                            participants_list.append(user)
                            name = user['name']
                            participants_names_list.append(name)
                            if user not in self.addable_users and user['id'] != self.user['id']:
                                self.addable_users_names.append(name)
                                self.addable_users.append(user)
                    else:
                        error = ErrorHandler(self.root, participants_response['error'])

                    # Получаем сообщения по id чата
                    messages = db.select_all_messages_by_chat_id(chat_id=chat_id)
                    if messages['isSuccess']:
                        messages_list = messages['data']
                        if len(messages_list) > 0:
                            last_message = messages_list[-1]['text']

                        # Создаём словарь с доступными чатами и необходимой информацией
                        self.available_chats[chat_id] = {'name': chat_name, 'last_message': last_message,
                                                         'participants_count': len(participants_list),
                                                         'participants': participants_list, 'participants_names': participants_names_list}

                    else:
                        error = ErrorHandler(self.root, messages['error'])
            for chat_id in self.available_chats:
                chat = self.available_chats[chat_id]
                self.add_selectable_chat_view(chat_id, DEFAULT_AVATAR_PATH, chat['name'], chat['last_message'])
        self.current_page.hide()
        self.chatting_page.show()
        self.current_page = self.chatting_page

    def switch_to_sign_up_page(self) -> None:
        self.current_page.hide()
        self.sign_up_page.show()
        self.current_page = self.sign_up_page

    def switch_to_adding_page(self) -> None:
        self.adding_page = AddingPage(self.root, self.switch_to_chatting_page, self.on_chat_adding_submit, self.addable_users, self.addable_users_names)
        self.current_page.hide()
        self.adding_page.show()
        self.current_page = self.adding_page

    def get_current_page(self) -> str:
        return self.current_page.name

    #################################################################################################
    # Методы обработчики добавления новых элементов UI
    #################################################################################################

    # Метод для добавления чата
    def on_chat_adding_submit(self) -> None:
        chat_type = self.adding_page.chat_type_choose_menu.get()
        chat_name = self.adding_page.chat_name_entry.get()
        participants_list = self.adding_page.selected_users_data
        participants_names_list = self.adding_page.selected_users_names
        participants_count = len(participants_list)
        avatar_url = self.adding_page.avatar_url_entry.get()
        if avatar_url == '':
            avatar_url = DEFAULT_AVATAR_PATH

        if chat_name != '' and participants_list:
            chat_response = db.chats.add(type=chat_type, name=chat_name, avatar_url=avatar_url)
            if chat_response['isSuccess']:
                chat_id = chat_response['data']['id']
                self.available_chats[chat_id] = {'name': chat_name, 'last_message': 'Начните общение!',
                                                 'participants_count': participants_count,
                                                 'participants': participants_list, 'participants_names': participants_names_list}
                self.add_selectable_chat_view(chat_id, avatar_url, chat_name, 'Начните общение')
                self.switch_to_chatting_page()
        else:
                self.adding_page.error_callback('Проверьте заполненность полей!')

    # Метод для отправки сообщения
    def send_message(self) -> None:
        text = self.current_chat_view.message_entry.get()

        if text != '':
            message_type = 'text'
            chat_id = self.current_chat_info['id']
            user_id = self.user['id']

            send_response = db.messages.add(type=message_type, text=text, chat_id=chat_id, user_id=user_id)
            if send_response['isSuccess']:
                self.add_message_view('text', text, 'Вы')
                self.current_chat_view.message_entry.delete(0, "end")
            else:
                error = ErrorHandler(self.root, 'Что-то пошло не так, проверьте Интернет-соединение.')

    # Метод для открытия чата
    def open_chat(self, chat_id) -> None:
        """
        Получаем информацию о чате из БД и передаём её

        :param chat_id: ID открываемого чата
        """

        if self.current_chat_info is None or chat_id != self.current_chat_info['id']:
            chat_type = 'group'  # В будущем изменить
            chat_name = self.available_chats[chat_id]['name']
            chat_participants_count = self.available_chats[chat_id]['participants_count']
            chat_participants_names = self.available_chats[chat_id]['participants_names']

            self.current_chat_info = {'id': chat_id,'type': chat_type, 'name': chat_name, 'participants_names': chat_participants_names, 'participants_count': chat_participants_count}

            self.add_chat_view('group', chat_name, chat_participants_count)

            chat_messages = db.select_all_messages_by_chat_id(chat_id=chat_id)
            if chat_messages['isSuccess']:
                for message in chat_messages['data']:
                    if message['file_id'] is not None:
                        content_type = 'image'
                        content = 'Пока без картинок'
                    else:
                        content_type = 'text'
                        content = message['text']

                    sender_response = db.select_by_id(id=message['user_id'])
                    if sender_response['isSuccess']:
                        sender_name = sender_response['data']['name']
                        if sender_response['data']['id'] == self.user['id']:
                            sender_name = 'Вы'
                    else:
                        sender_name = ''
                        error = ErrorHandler(self.root, sender_response['error'])
                    self.add_message_view(content_type, content, sender_name)
            else:
                error = ErrorHandler(self.root, chat_messages['error'])

#################################################################################################
    # Методы добавление UI
#################################################################################################

    # Добавление вида выбранного чата (тип чата, имя чата, количество участников)
    def add_chat_view(self, chat_type: str, name: str, participants_count: int):
        self.current_chat_view = ChatView(self.chatting_page, chat_type, name, participants_count, DEFAULT_AVATAR_PATH, self.send_message, self.see_chat_info)
        self.chatting_page.on_chat_selection()
        self.current_chat_view.grid(column=1, row=0, sticky="nsew")

    # Добавление вида чата на панели списка чатов
    def add_selectable_chat_view(self, chat_id: int, avatar_url: str, name: str, last_message: str) -> None:
        selectable_chat = SelectableChatView(self.chatting_page.chats_list_scrollable_frame, avatar_url, name, last_message)
        selectable_chat.bind("<Button-1>", command=lambda event: self.open_chat(chat_id))
        selectable_chat.pack(side='top', anchor='ne', pady=5, padx=5, fill="x")

    # Добавление вида сообщения
    def add_message_view(self, content_type: str, content: str, sender_name: str) -> None:
        message = MessageView(self.current_chat_view.messages_frame, content_type, content, sender_name)
        message.pack(side='top', anchor='se', pady=5, padx=5, expand=True)

    def see_chat_info(self, event) -> None:
        current_chat_info_window = ChatInfoView(self.chatting_page, self.current_chat_view, self.current_chat_info['participants_names'])
        current_chat_info_window.focus()

#################################################################################################
    # Функции для авторизации
#################################################################################################

    def register_user(self) -> None:
        name = self.sign_up_page.name_entry.get()
        username = self.sign_up_page.username_entry.get()
        password = self.sign_up_page.password_entry.get()
        password_confirm = self.sign_up_page.password_confirm_entry.get()
        if name != '' and username != '' and password != '' and password_confirm != '':
            if password == password_confirm:
                if not db.users.exists(username=username):
                    register_response = db.users.add(name=name, username=username, password=password)
                    if register_response['isSuccess']:
                        self.user = register_response['data']

                        self.chatting_page = ChattingPage(self.root, self.switch_to_adding_page, self.user)
                        self.switch_to_chatting_page()

                        self.is_authorized = True
                    else:
                        error = ErrorHandler(self.root, register_response['error'])
                else:
                    self.sign_up_page.error_callback('Такое имя пользователя занято!')
            else:
                self.sign_up_page.error_callback('Пароли не совпадают!')
        else:
            self.sign_up_page.error_callback('Проверьте заполненность полей!')

    def login_user(self) -> None:
        username = self.sign_up_page.username_entry.get()
        password = self.sign_up_page.password_entry.get()
        if username != '' and password != '':
            is_existing = db.users.exists(username=username, password=password)
            if is_existing:
                # Получение словаря в user_response['data'], где есть id и name
                login_response = db.select_by_username(username=username)
                if login_response['isSuccess']:
                    self.user = login_response['data']

                    self.chatting_page = ChattingPage(self.root, self.switch_to_adding_page, self.user)
                    self.switch_to_chatting_page()

                    self.is_authorized = True
                else:
                    error = ErrorHandler(self.root, login_response['error'])
            else:
                self.sign_up_page.error_callback('Неправильный username или пароль')
        else:
            self.sign_up_page.error_callback('Проверьте заполненность полей!')

#################################################################################################

    def initialize(self):
        self.start_page.show()
        self.root.after(2000, self.switch_to_sign_up_page)

    def run(self):
        self.initialize()
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()
