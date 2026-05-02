import customtkinter as ctk


class AddingPage(ctk.CTkFrame):
    def __init__(self, master, back_to_chats, on_chat_adding_submit, addable_users):
        # Инициализируем как CTkFrame
        super().__init__(master, corner_radius=0)

        # Имя страницы
        self.name = 'adding_page'

        self.returning = back_to_chats
        self.submitting = on_chat_adding_submit
        self.users_names = addable_users

        self.selected_users = []  # Список строк (имен)
        self.user_widgets = []  # Список созданных виджетов (фреймов со строками)

        self.grid_columnconfigure((0, 3), weight=1)
        self.grid_rowconfigure((0, 12), weight=1)

        # Заголовок страницы
        self.title_label = ctk.CTkLabel(
            self,
            text="Создание нового чата",
            font=("Arial", 24, "bold")
        )

        self.chat_type_label = ctk.CTkLabel(
            self,
            text="Выберите тип чата:",
            font=("Arial", 14)
        )

        self.chat_type_choose_menu = ctk.CTkOptionMenu(
            self,
            width=300,
            height=50,
            values = ["Личная переписка", "Группа", "Канал"]
        )

        self.chat_name_label = ctk.CTkLabel(
            self,
            text='Название чата:',
            font=("Arial", 14)
        )

        self.chat_name_entry = ctk.CTkEntry(
            self,
            width=400,
            height=40,
            placeholder_text="Например: Проект Альфа"
        )

        self.participants_label = ctk.CTkLabel(
            self,
            text='Выберите участников:',
            font=("Arial", 14)
        )

        self.participants_combo_box = ctk.CTkComboBox(
            self,
            width=400,
            height=40,
            values=self.users_names,
            command=self.add_participant  # Привязываем функцию
        )
        self.participants_combo_box.set('')
        self.participants_combo_box._entry.bind("<KeyRelease>", self.filter_users)

        self.participants_list_frame = ctk.CTkScrollableFrame(
            self,
            width=400,
            height=100,
            label_text="Выбранные участники"
        )

        self.avatar_url_label = ctk.CTkLabel(
            self,
            text="Ссылка на изображение:",
            font=("Arial", 14)
        )

        self.avatar_url_entry = ctk.CTkEntry(
            self,
            width=400,
            height=40,
            placeholder_text="Вставьте сюда ссылку на изображение для аватара чата"
        )

        # Кнопки с использованием относительных координат для адаптивности
        self.back_button = ctk.CTkButton(
            self,
            text="Вернуться к чатам",
            fg_color="transparent",
            border_width=2,
            width=200,
            height=45,
            command=self.returning
        )

        self.submit_button = ctk.CTkButton(
            self,
            text="Создать чат",
            width=200,
            height=45,
            command=self.submitting
        )

        self.error_label = ctk.CTkLabel(
            self,
            text='',
            text_color="red"
        )

        self.setup_initial_view()

    def add_participant(self, choice):
        if choice and choice not in self.selected_users and choice in self.users_names:
            self.selected_users.append(choice)
            self.render_user_row(choice)

        # Очищаем поле и возвращаем полный список для следующего поиска
        self.participants_combo_box.set("")
        self.participants_combo_box.configure(values=self.users_names)

    def render_user_row(self, name):
        # Создаем контейнер для одной строки (имя + кнопка)
        row = ctk.CTkFrame(self.participants_list_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)

        name_label = ctk.CTkLabel(row, text=name, font=("Arial", 12))
        name_label.pack(side="left", padx=10)

        # Кнопка удаления
        del_btn = ctk.CTkButton(
            row,
            text="✕",
            width=25,
            height=25,
            fg_color="#ff4d4d",
            hover_color="#cc0000",
            command=lambda n=name, r=row: self.remove_user(n, r)
        )
        del_btn.pack(side="right", padx=5)

        # Сохраняем ссылку, чтобы можно было очистить всё разом если нужно
        self.user_widgets.append(row)

    def remove_user(self, name, row_widget):
        if name in self.selected_users:
            self.selected_users.remove(name)
        row_widget.destroy()

    def filter_users(self, event):
        # Получаем текст, который ввел пользователь
        typed_text = self.participants_combo_box.get().lower()

        if typed_text == "":
            # Если пусто — показываем всех
            filtered_values = self.users_names
        else:
            # Фильтруем список по вхождению подстроки
            filtered_values = [
                name for name in self.users_names
                if typed_text in name.lower()
            ]

        # Обновляем список в выпадающем меню
        self.participants_combo_box.configure(values=filtered_values)

    def setup_initial_view(self):
        self.grid_rowconfigure(7, minsize=120)

        self.title_label.grid(row=0, column=1, columnspan=2, pady=(40, 20))

        self.chat_type_label.grid(row=1, column=1, columnspan=2, pady=(10, 0))
        self.chat_type_choose_menu.grid(row=2, columnspan=2, column=1, pady=10)

        self.chat_name_label.grid(row=3, column=1, columnspan=2, pady=(10, 0))
        self.chat_name_entry.grid(row=4, column=1, columnspan=2, pady=10)

        self.participants_label.grid(row=5, column=1, columnspan=2, pady=(10, 0))
        self.participants_combo_box.grid(row=6, column=1, columnspan=2, pady=10)

        self.participants_list_frame.grid(row=7, column=1, columnspan=2, pady=(5, 10), sticky='n')

        self.avatar_url_label.grid(row=8, column=1, columnspan=2, pady=(10, 0))
        self.avatar_url_entry.grid(row=9, column=1, columnspan=2, pady=10)

        self.error_label.grid(row=10, column=1, columnspan=2, pady=5)

        self.back_button.grid(row=11, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.submit_button.grid(row=11, column=2, padx=(10, 0), pady=10, sticky="nsew")

    def error_callback(self, error):
        self.error_label.configure(text=error)

    def show(self):
        self.pack(expand=True, fill="both")
        self.error_label.configure(text='')

    def hide(self):
        self.pack_forget()
