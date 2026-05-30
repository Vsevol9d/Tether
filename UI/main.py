import customtkinter as ctk
import asyncio
from async_tkinter_loop import async_mainloop, async_handler
import sys, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_AVATAR_PATH = str(BASE_DIR / "assets" / "default_avatar.jpg")

sys.path.append(os.path.abspath("../Database"))
sys.path.append(os.path.abspath("../OnlineServer"))

from UI.pages.start_page import StartPage
from UI.pages.chatting_page import ChattingPage
from UI.pages.adding_page import AddingPage
from UI.pages.sign_up_page import SignUpPage
from UI.element_views.chat_view import MessageView, ChatView, ChatInfoView
from UI.element_views.selectable_chat_view import SelectableChatView
from server_api import ServerAPI

# Обработчик ошибок со стороны UI
from error_handler import ErrorHandler

# Настройка внешнего вида (можно вынести в initialize)
ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна приложения
        self.geometry("800x600")
        self.title("Tether")

        # Настройка минимальных размеров окна (опционально)
        self.minsize(600, 400)

        # Центрирование окна на экране
        self.center_window()

        self.server_api = None

        self.user = None
        self.available_chats = {}
        self.current_chat_view = None
        self.current_chat_info = None
        self.chats_info_loaded = False

        # Инициализация классов страниц
        self.start_page = StartPage(self)
        self.sign_up_page = SignUpPage(self, self.register_user, self.login_user)

        self.current_page = self.start_page

        # Страницы для которых требуются данные из БД, инициализируются позже
        self.chatting_page = None
        self.adding_page = None

    def center_window(self):
        """Центрирует окно приложения на экране."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    async def switch_to_chatting_page(self):
        """Переключение на страницу с чатами"""
        if not self.chats_info_loaded:
            response = await self.server_api.get_user_chats(str(self.user['id']))

            if response and response.get('isSuccess'):
                chats = response.get('data', [])

                # Загружаем данные по каждому чату
                for chat in chats:
                    await self._process_chat_data(chat)

                # Отрисовка чатов
                for chat_id, chat in self.available_chats.items():
                    self.add_selectable_chat_view(
                        chat_id=chat_id,
                        avatar_url=chat.get('avatar_url'),
                        name=chat.get('name'),
                        last_message=chat.get('last_mes'),
                        is_new=chat.get('is_new')
                    )

        self.chats_info_loaded = True
        self.current_page.hide()
        if self.chatting_page:
            self.chatting_page.show()
            self.current_page = self.chatting_page

    async def _process_chat_data(self, chat: dict):
        """Обработка данных чата"""
        chat_id = chat.get('id')
        participants = []
        is_new = True

        # Получаем последнее сообщение
        last_mes = chat.get('last_mes')
        last_user_name = chat.get('last_user_name')

        if not last_mes:
            last_mes = 'Начните общение'

        if last_user_name:
            last_message_full = last_user_name + ': ' + last_mes
        else:
            last_message_full = last_mes

        if chat.get('avatar_url'):
            avatar_url = chat.get('avatar_url')
        else:
            avatar_url = DEFAULT_AVATAR_PATH

        # Получаем участников
        participants_response = await self.server_api.get_chat_data(chat_id)

        if participants_response and participants_response.get('isSuccess'):
            participants = participants_response.get('data', []) # Информация об участниках чата (id, name, avatar_url, last_time_online)

        self.available_chats[chat_id] = {
            'id': chat_id,
            'name': chat.get('name', 'Чат'),
            'avatar_url': avatar_url,
            'type': chat.get('type', 'group'),
            'last_mes': last_message_full,
            'last_user_name': last_user_name,
            'is_new': is_new,
            'participants': [participants],
            'participants_names': [user['name'] for user in participants]
        }

    def switch_to_sign_up_page(self) -> None:
        """Метод для переключения на страницу авторизации"""
        self.current_page.hide()
        self.sign_up_page.show()
        self.current_page = self.sign_up_page

    def switch_to_adding_page(self) -> None:
        """Метод для переключения на страницу для добавления чата"""
        self.adding_page = AddingPage(self, self.switch_to_chatting_page, self.on_chat_adding_submit,
                                      self.addable_users, self.addable_users_names)
        self.current_page.hide()
        self.adding_page.show()
        self.current_page = self.adding_page

    def get_current_page(self) -> str:
        """Метод для получения имени текущей страницы"""
        return self.current_page.name

    #################################################################################################
    # Методы обработчики добавления новых элементов UI
    #################################################################################################

    async def on_chat_adding_submit(self):
        """Создание нового чата"""
        chat_type = self.adding_page.chat_type_choose_menu.get()
        chat_name = self.adding_page.chat_name_entry.get().strip()
        avatar_url = self.adding_page.avatar_url_entry.get().strip() or DEFAULT_AVATAR_PATH
        participants_data = self.adding_page.selected_users_data
        participants_names = self.adding_page.selected_users_names

        if not chat_name:
            self.adding_page.error_callback('Введите название чата!')
            return

        # Создаем чат
        response = await self.server_api.create_chat(chat_type, chat_name, avatar_url)

        if response and response.get('isSuccess'):
            chat_id = response.get('data', {}).get('id')

            self.available_chats[chat_id] = {
                'id': chat_id,
                'type': chat_type,
                'name': chat_name,
                'last_message': 'Начните общение!',
                'is_new': True,
                'participants': participants_data,
                'participants_names': participants_names
            }

            self.add_selectable_chat_view(chat_id, avatar_url, chat_name, 'Начните общение!', is_new=True)
            await self.switch_to_chatting_page()
        else:
            error_msg = response.get('error', 'Ошибка создания чата') if response else 'Ошибка соединения'
            self.adding_page.error_callback(error_msg)

    # Метод для отправки сообщения
    async def send_message(self):
        """Отправка сообщения"""
        text = self.current_chat_view.message_entry.get().strip()
        if not text:
            return

        chat_id = self.current_chat_info['id']
        user_id = self.user['id']

        self.current_chat_view.message_entry.delete(0, "end")

        response = await self.server_api.send_message('text', text, str(chat_id), str(user_id))

        if response and response.get('isSuccess'):
            if self.current_chat_info['is_new']:
                self.current_chat_view.on_first_message_sending()
                self.current_chat_info['is_new'] = False
            self.add_message_view('text', text, 'Вы')
        else:
            self.current_chat_view.message_entry.insert(0, text)
            error_msg = response.get('error', 'Ошибка отправки') if response else 'Ошибка соединения'
            ErrorHandler(self, error_msg)

    async def open_chat(self, chat_id, is_new: bool):
        """Открытие чата"""
        if self.current_chat_info and chat_id == self.current_chat_info['id']:
            return

        chat_data = self.available_chats[chat_id]

        # Получаем данные чата
        chat_info_response = await self.server_api.get_chat_data(str(chat_id))

        chat_name = chat_data['name']
        chat_type = chat_data['type']

        if chat_info_response and chat_info_response.get('isSuccess'):
            chat_info = chat_info_response.get('data', {})
            chat_name = chat_info.get('name', chat_name)
            chat_type = chat_info.get('type', chat_type)

        self.current_chat_info = {
            'id': chat_id,
            'type': chat_type,
            'name': chat_name,
            'participants_names': chat_data.get('participants_names', []),
            'participants_count': len(chat_data.get('participants', [])),
            'is_new': is_new
        }

        self.add_chat_view(chat_type, chat_name, self.current_chat_info['participants_count'], is_new)

        if not is_new:
            # Загружаем сообщения
            response = await self.server_api.get_messages(str(chat_id))

            if response and response.get('isSuccess'):
                messages = response.get('data', [])
                for message in messages:
                    sender_name = 'Вы' if message.get('user_id') == self.user['id'] else 'Пользователь'
                    content = message.get('text', '')
                    self.add_message_view('text', content, sender_name)

    #################################################################################################
    # Методы добавление UI
    #################################################################################################

    # Добавление вида выбранного чата (тип чата, имя чата, количество участников)
    def add_chat_view(self, chat_type: str, name: str, participants_count: int, is_new: bool) -> None:
        """Метод, отвечающий за добавление видимого чата с перепиской"""
        if self.current_chat_view is None:
            self.chatting_page.on_chat_selection()

        self.current_chat_view = ChatView(self.chatting_page, chat_type, name, participants_count, DEFAULT_AVATAR_PATH,
                                          self.send_message, self.see_chat_info)
        print(is_new)

        if is_new:
            self.current_chat_view.on_new_chat_selection()

        self.current_chat_view.grid(column=1, row=0, sticky="nsew")

    # Добавление вида чата на панели списка чатов
    def add_selectable_chat_view(self, chat_id: int, avatar_url: str, name: str, last_message: str,
                                 is_new=False) -> None:
        """Метод, отвечающий за добавление видимого чата в списке чатов"""
        selectable_chat = SelectableChatView(self.chatting_page.chats_list_scrollable_frame, avatar_url, name,
                                             last_message)
        selectable_chat.bind("<Button-1>", command=async_handler(lambda event: self.open_chat(chat_id, is_new)))
        selectable_chat.pack(side='top', anchor='ne', pady=5, padx=5, fill="x")

    # Добавление вида сообщения
    def add_message_view(self, content_type: str, content: str, sender_name: str) -> None:
        """Метод, отвечающий за добавление видимого сообщения в специальный контейнер в окне в видимым чатом"""
        message = MessageView(self.current_chat_view.messages_frame, content_type, content, sender_name)
        message.pack(side='top', anchor='se', pady=5, padx=5, expand=True)

    def see_chat_info(self, event) -> None:
        """Метод, отвечающий за отображение информации по нажатии на шапку чата"""
        current_chat_info_window = ChatInfoView(self.chatting_page, self.current_chat_view,
                                                self.current_chat_info['participants_names'])
        current_chat_info_window.focus()

    #################################################################################################
    # Функции для авторизации
    #################################################################################################

    async def register_user(self):
        """Регистрация через сервер"""
        name = self.sign_up_page.name_entry.get().strip()
        username = self.sign_up_page.username_entry.get().strip()
        password = self.sign_up_page.password_entry.get()
        password_confirm = self.sign_up_page.password_confirm_entry.get()

        if not all([name, username, password, password_confirm]):
            self.sign_up_page.error_callback('Проверьте заполненность полей!')
            return

        if password != password_confirm:
            self.sign_up_page.error_callback('Пароли не совпадают!')
            return

        # Прямой вызов - ответ содержит isSuccess, data, error
        response = await self.server_api.register_user(name, username, password)

        if response and response.get('isSuccess'):
            self.user = response.get('data')
            self.chatting_page = ChattingPage(self, self.switch_to_adding_page, self.user)
            await self.switch_to_chatting_page()
        else:
            error_msg = response.get('error', 'Ошибка регистрации') if response else 'Ошибка соединения'
            self.sign_up_page.error_callback(error_msg)

    async def login_user(self):
        """Вход через сервер"""
        username = self.sign_up_page.username_entry.get().strip()
        password = self.sign_up_page.password_entry.get()

        if not all([username, password]):
            self.sign_up_page.error_callback('Проверьте заполненность полей!')
            return

        response = await self.server_api.login_user(username, password)

        if response and response.get('isSuccess'):
            self.user = response.get('data')
            self.chatting_page = ChattingPage(self, self.switch_to_adding_page, self.user)
            await self.switch_to_chatting_page()
        else:
            error_msg = response.get('error', 'Неверный username или пароль') if response else 'Ошибка соединения'
            self.sign_up_page.error_callback(error_msg)

    #################################################################################################

    async def initialize(self):
        """Инициализация с подключением к серверу"""
        self.server_api = await ServerAPI().connect()
        self.deiconify()
        self.lift()
        self.focus_force()
        self.start_page.show()
        await asyncio.sleep(2.0)
        self.switch_to_sign_up_page()

    def run(self) -> None:
        """Запуск приложения"""
        self.withdraw()
        self.after_idle(async_handler(self.initialize))
        async_mainloop(self)


if __name__ == "__main__":
    app = App()
    app.run()