import customtkinter as ctk
from PIL import Image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MENU_ICON_PATH = BASE_DIR / "assets" / "menu_icon.png"

class ChattingPage(ctk.CTkFrame):
    def __init__(self, master, switch_to_adding_page, user_info):
        """
        Класс вмещающий в себя окно со списком чатов и выбранным чатом.

        :param master: Главное окно (ctk.Ctk) приложения в main
        :param switch_to_adding_page: Метод для перехода в окно добавления нового чата в main
        """
        super().__init__(master, corner_radius=0)

        # Имя страницы
        self.name = 'chatting_page'

        self.master = master
        self.switch_to_adding_chat = switch_to_adding_page
        self.user_info = user_info

######### --- Левая панель: список чатов --- #########

        # Рамка для размещения списка чатов
        self.chats_list_frame = ctk.CTkFrame(
            self,
            width=300,
            corner_radius=0,
            border_width=1,
            border_color="gray"
        )
        self.chats_list_frame.grid_propagate(False)

        # Область для самого списка чатов
        self.chats_list_scrollable_frame = ctk.CTkScrollableFrame(
            self.chats_list_frame,
            height=540,
            border_width=1
        )

        # Кнопка добавления нового чата
        self.add_new_chat_button = ctk.CTkButton(
            self.chats_list_frame,
            height=40,
            text='Добавить новый чат',
            command=self.switch_to_adding_chat
        )

        self.menu_icon_image = Image.open(MENU_ICON_PATH)
        self.menu_icon_sized = ctk.CTkImage(dark_image=self.menu_icon_image, size=(30, 30))

        self.view_user_information_frame = ctk.CTkFrame(
            self.chats_list_frame,
            height=30
        )
        self.view_user_information_frame.grid_propagate(False)

        self.menu_icon = ctk.CTkLabel(
            self.view_user_information_frame,
            text='',
            image=self.menu_icon_sized
        )

        self.user_name_label = ctk.CTkLabel(
            self.view_user_information_frame,
            text='',
            font=('Arial', 12)
        )

        def on_enter(event):
            self.user_name_label.configure(text=user_info['name'])

        def on_leave(event):
            self.user_name_label.configure(text='')

        self.menu_icon.bind("<Enter>", on_enter)
        self.menu_icon.bind("<Leave>", on_leave)

######### --- Правая панель: окно чата --- #########

        # Рамка для выбранного чата
        self.default_chat_frame = ctk.CTkFrame(
            self,
            width=500,
            corner_radius=0,
            border_width=1,
            border_color="gray",
            fg_color="#696969"
        )
        self.default_chat_frame.grid_propagate(False)

        self.choose_label = ctk.CTkLabel(
            self.default_chat_frame,
            font=("Arial", 12),
            fg_color="#2E2E2E",
            corner_radius=5,
            text='Пожалуйста, выберите чат для переписки'
        )

        self.setup_initial_view()

    def setup_initial_view(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Упаковка рамки со списком чатов
        self.chats_list_frame.grid(column=0, row=0, sticky="nsew")

        self.chats_list_frame.grid_columnconfigure(0, weight=1)
        self.chats_list_frame.grid_rowconfigure(1, weight=1)
        self.chats_list_frame.grid_rowconfigure((0, 2), weight=0)

        # Упаковка рамки с информацией о пользователе
        self.view_user_information_frame.grid(column=0, row=0, sticky="we", padx=5, pady=5)

        # Упаковка рамки со списком доступных чатов
        self.chats_list_scrollable_frame.grid(column=0, row=1, sticky="nsew", pady=5, padx=5)

        # Упаковка кнопки для перехода на страницу добавления нового чата
        self.add_new_chat_button.grid(column=0, row=2, sticky="sew", padx=5, pady=5)

        # Упаковка элементов рамки с информацией о пользователе
        self.menu_icon.pack(side="left")
        self.user_name_label.pack(side="left", padx=5)

        # Упаковка выбранного чата
        self.default_chat_frame.grid(column=1, row=0, sticky="nsew")

        self.default_chat_frame.grid_columnconfigure(0, weight=1)
        self.default_chat_frame.grid_rowconfigure(0, weight=1)

        # Упаковка надписи с предложением выбрать чат
        self.choose_label.grid(column=0, row=0, ipady=5, ipadx=5)

    def on_chat_selection(self):
        """
        Убирает стандартное окно с предложением выбрать чат
        :return: None
        """
        self.default_chat_frame.destroy()
        self.choose_label.destroy()

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()
