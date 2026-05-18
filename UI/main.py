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
from Database.api import Session, DataBase

# Обработчик ошибок со стороны UI
from error_handler import ErrorHandler

with Session() as session:
    db = DataBase(session)

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

        self.user = None
        self.available_chats = {}
        self.current_chat_view = None
        self.current_chat_info = None
        self.is_authorized = False
        self.user_info_loaded = False
        self.addable_users_names = []
        self.addable_users = []

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

    async def _run_db_operation(self, operation, *args, **kwargs):
        """Универсальный метод для выполнения синхронных операций БД в отдельном потоке."""
        return await asyncio.to_thread(operation, *args, **kwargs)

    async def switch_to_chatting_page(self) -> None:
        if not self.user_info_loaded:
            chats = await self._run_db_operation(db.select_all_chats_by_id_user, user_id=self.user['id'])

            if chats['isSuccess']:
                # Создаем список задач для параллельного выполнения
                tasks = []
                for chat in chats['data']:
                    tasks.append(self._process_chat_data(chat))

                # Запускаем сбор данных по всем чатам одновременно
                await asyncio.gather(*tasks)

            # Отрисовка интерфейса (остается синхронной)
            for chat_id, chat in self.available_chats.items():
                self.add_selectable_chat_view(
                    chat_id,
                    DEFAULT_AVATAR_PATH,
                    chat['name'],
                    chat['last_message'],
                    is_new=chat['is_new']
                )

        # Переключение страниц (UI операции обычно синхронны)
        self.user_info_loaded = True
        self.current_page.hide()
        self.chatting_page.show()
        self.current_page = self.chatting_page

    async def _process_chat_data(self, chat: dict) -> None:
        """Вспомогательный метод для обработки одного чата."""
        chat_id = chat['id']

        # Запускаем запросы к участникам и сообщениям параллельно для одного чата
        participants_task = self._run_db_operation(db.select_all_users_by_chat_id, chat_id=chat_id)
        messages_task = self._run_db_operation(db.select_all_messages_by_chat_id, chat_id=chat_id)

        participants_response, messages = await asyncio.gather(participants_task, messages_task)

        participants_list = []
        participants_names_list = []

        # Обработка участников
        if participants_response['isSuccess']:
            for user in participants_response['data']:
                participants_list.append(user)
                name = user['name']
                participants_names_list.append(name)

                if user not in self.addable_users and user['id'] != self.user['id']:
                    self.addable_users_names.append(name)
                    self.addable_users.append(user)
        else:
            ErrorHandler(self, participants_response['error'])

        # Обработка сообщений
        if messages['isSuccess']:
            messages_list = messages['data']
            if len(messages_list) > 0:
                last_message = messages_list[-1]['text']
                is_new = False
            else:
                last_message = 'Начните общение'
                is_new = True

            self.available_chats[chat_id] = {
                'type': chat['type'],
                'name': chat['name'],
                'last_message': last_message,
                'participants_count': len(participants_list),
                'is_new': is_new,
                'participants': participants_list,
                'participants_names': participants_names_list
            }
        else:
            ErrorHandler(self, messages['error'])

    def switch_to_sign_up_page(self) -> None:
        self.current_page.hide()
        self.sign_up_page.show()
        self.current_page = self.sign_up_page

    def switch_to_adding_page(self) -> None:
        self.adding_page = AddingPage(self, self.switch_to_chatting_page, self.on_chat_adding_submit,
                                      self.addable_users, self.addable_users_names)
        self.current_page.hide()
        self.adding_page.show()
        self.current_page = self.adding_page

    def get_current_page(self) -> str:
        return self.current_page.name

    #################################################################################################
    # Методы обработчики добавления новых элементов UI
    #################################################################################################

    # Метод для добавления чата
    async def on_chat_adding_submit(self) -> None:
        chat_type = self.adding_page.chat_type_choose_menu.get()
        chat_name = self.adding_page.chat_name_entry.get().strip()
        avatar_url = self.adding_page.avatar_url_entry.get().strip()

        if not avatar_url:
            avatar_url = DEFAULT_AVATAR_PATH

        participants_list = self.adding_page.selected_users_data + [self.user]
        participants_names_list = self.adding_page.selected_users_names + [self.user['name']]
        participants_count = len(participants_list)

        # Проверка на заполненность обязательных полей
        if not chat_name or not self.adding_page.selected_users_data:
            self.adding_page.error_callback('Проверьте заполненность полей!')
            return

        # Добавление чата в БД
        chat_response = await self._run_db_operation(db.chats.add, type=chat_type, name=chat_name,
                                                     avatar_url=avatar_url)

        if chat_response['isSuccess']:
            chat_id = chat_response['data']['id']

            # Локальное сохранение данных о новом чате
            self.available_chats[chat_id] = {
                'type': chat_type,
                'name': chat_name,
                'last_message': 'Начните общение!',
                'participants_count': participants_count,
                'is_new': True,
                'participants': participants_list,
                'participants_names': participants_names_list
            }

            # Отрисовка элемента чата в UI
            self.add_selectable_chat_view(chat_id, avatar_url, chat_name, 'Начните общение!', is_new=True)

            await self.switch_to_chatting_page()
        else:
            # Если в ответе БД заложена ошибка, выводим её через обработчик
            ErrorHandler(self, chat_response['error'])

    # Метод для отправки сообщения
    async def send_message(self) -> None:
        # Получаем текст и очищаем его от случайных пробелов по краям
        text = self.current_chat_view.message_entry.get().strip()

        if not text:
            return

        message_type = 'text'
        chat_id = self.current_chat_info['id']
        is_new = self.current_chat_info['is_new']
        user_id = self.user['id']

        # Очищаем поле ввода сразу
        self.current_chat_view.message_entry.delete(0, "end")

        # Асинхронная отправка сообщения в базу данных
        send_response = await self._run_db_operation(db.messages.add, type=message_type, text=text, chat_id=chat_id,
                                                     user_id=user_id)

        if send_response['isSuccess']:
            if is_new:
                self.current_chat_view.on_first_message_sending()
                self.current_chat_info['is_new'] = False

            # Отображаем новое сообщение в интерфейсе
            self.add_message_view('text', text, 'Вы')
        else:
            # Если произошла ошибка, возвращаем текст назад в поле ввода и показываем ошибку
            self.current_chat_view.message_entry.insert(0, text)
            ErrorHandler(self, send_response['error'])

    # Метод для открытия чата
    async def open_chat(self, chat_id, is_new: bool) -> None:
        """
        Получаем информацию о чате из БД и передаём её

        :param chat_id: ID открываемого чата
        :param is_new: Новый ли чат или нет
        """
        # Если чат уже открыт, ничего не делаем
        if self.current_chat_info is not None and chat_id == self.current_chat_info['id']:
            return

        chat_type = self.available_chats[chat_id]['type']
        chat_name = self.available_chats[chat_id]['name']
        chat_participants_names = self.available_chats[chat_id]['participants_names']

        if chat_type != 'private':
            chat_participants_count = self.available_chats[chat_id]['participants_count']
        else:
            chat_participants_count = 2

        self.current_chat_info = {
            'id': chat_id, 'type': chat_type, 'name': chat_name,
            'participants_names': chat_participants_names,
            'participants_count': chat_participants_count, 'is_new': is_new
        }

        # Отображаем пустую страницу чата
        self.add_chat_view(chat_type=chat_type, name=chat_name, participants_count=chat_participants_count,
                           is_new=is_new)

        if not is_new:
            # Асинхронно получаем все сообщения чата
            chat_messages = await self._run_db_operation(db.select_all_messages_by_chat_id, chat_id=chat_id)

            if chat_messages['isSuccess']:
                messages_data = chat_messages['data']

                # Собираем все уникальные ID отправителей, чтобы загрузить их за один раз
                unique_sender_ids = {msg['user_id'] for msg in messages_data}

                # Запускаем параллельный фоновый сбор данных обо всех авторах
                sender_tasks = {uid: self._run_db_operation(db.select_by_id, id=uid) for uid in unique_sender_ids}
                sender_results = await asyncio.gather(*sender_tasks.values())

                # Создаем словарь {user_id: name} для быстрой подстановки имен
                senders_cache = {}
                for user_id, response in zip(sender_tasks.keys(), sender_results):
                    if response['isSuccess']:
                        senders_cache[user_id] = response['data']['name']
                    else:
                        senders_cache[user_id] = ''
                        ErrorHandler(self, response['error'])

                # Теперь быстро и без задержек отрисовываем сообщения из кэша
                for message in messages_data:
                    sender_id = message['user_id']
                    content_type = message['type']
                    content = message['text'] if content_type == 'text' else message['file_id']

                    # Определяем имя отправителя
                    if sender_id == self.user['id']:
                        sender_name = 'Вы'
                    else:
                        sender_name = senders_cache.get(sender_id, '')

                    self.add_message_view(content_type, content, sender_name)
            else:
                ErrorHandler(self, chat_messages['error'])

    #################################################################################################
    # Методы добавление UI
    #################################################################################################

    # Добавление вида выбранного чата (тип чата, имя чата, количество участников)
    def add_chat_view(self, chat_type: str, name: str, participants_count: int, is_new: bool) -> None:
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
        selectable_chat = SelectableChatView(self.chatting_page.chats_list_scrollable_frame, avatar_url, name,
                                             last_message)
        selectable_chat.bind("<Button-1>", command=async_handler(lambda event: self.open_chat(chat_id, is_new)))
        selectable_chat.pack(side='top', anchor='ne', pady=5, padx=5, fill="x")

    # Добавление вида сообщения
    def add_message_view(self, content_type: str, content: str, sender_name: str) -> None:
        message = MessageView(self.current_chat_view.messages_frame, content_type, content, sender_name)
        message.pack(side='top', anchor='se', pady=5, padx=5, expand=True)

    def see_chat_info(self, event) -> None:
        current_chat_info_window = ChatInfoView(self.chatting_page, self.current_chat_view,
                                                self.current_chat_info['participants_names'])
        current_chat_info_window.focus()

    #################################################################################################
    # Функции для авторизации
    #################################################################################################

    async def register_user(self) -> None:
        name = self.sign_up_page.name_entry.get().strip()
        username = self.sign_up_page.username_entry.get().strip()
        password = self.sign_up_page.password_entry.get()
        password_confirm = self.sign_up_page.password_confirm_entry.get()

        # Проверка на заполненность полей
        if not all([name, username, password, password_confirm]):
            self.sign_up_page.error_callback('Проверьте заполненность полей!')
            return

        # Проверка совпадения паролей
        if password != password_confirm:
            self.sign_up_page.error_callback('Пароли не совпадают!')
            return

        # Асинхронная проверка существования пользователя
        user_exists = await self._run_db_operation(db.users.exists, username=username)
        if user_exists:
            self.sign_up_page.error_callback('Такое имя пользователя занято!')
            return

        # Асинхронное добавление пользователя в БД
        register_response = await self._run_db_operation(db.users.add, name=name, username=username, password=password)
        if register_response['isSuccess']:
            self.user = register_response['data']
            self.is_authorized = True

            # Инициализация страницы чатов
            self.chatting_page = ChattingPage(self, self.switch_to_adding_page, self.user)

            await self.switch_to_chatting_page()
        else:
            ErrorHandler(self, register_response['error'])

    async def login_user(self) -> None:
        username = self.sign_up_page.username_entry.get().strip()
        password = self.sign_up_page.password_entry.get()

        # Проверка на заполненность полей
        if not all([username, password]):
            self.sign_up_page.error_callback('Проверьте заполненность полей!')
            return

        # Асинхронная проверка существования пользователя с таким паролем
        is_existing = await self._run_db_operation(db.users.exists, username=username, password=password)
        if not is_existing:
            self.sign_up_page.error_callback('Неправильный username или пароль')
            return

        # Асинхронное получение данных пользователя
        login_response = await self._run_db_operation(db.select_user_by_username, username=username)
        if login_response['isSuccess']:
            self.user = login_response['data']
            self.is_authorized = True

            # Инициализация страницы чатов
            self.chatting_page = ChattingPage(self, self.switch_to_adding_page, self.user)
            # Обязательно await для переключения страницы
            await self.switch_to_chatting_page()
        else:
            ErrorHandler(self, login_response['error'])

    #################################################################################################

    async def initialize(self) -> None:
        """Асинхронная инициализация приложения."""
        # Принудительно показываем окно
        self.deiconify()
        self.lift()
        self.focus_force()

        self.start_page.show()

        await asyncio.sleep(2.0)

        self.switch_to_sign_up_page()

    def run(self) -> None:
        """Запуск главного цикла приложения."""
        # Скрываем окно до полной инициализации
        self.withdraw()

        # Запускаем асинхронную инициализацию
        self.after_idle(async_handler(self.initialize))

        # Запускаем асинхронный главный цикл
        async_mainloop(self)


if __name__ == "__main__":
    app = App()
    app.run()