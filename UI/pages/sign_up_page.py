import customtkinter as ctk

class SignUpPage(ctk.CTkFrame):
    def __init__(self, master, register_method, login_method):
        # Инициализируем сам класс как CTkFrame
        super().__init__(master, corner_radius=15)

        # Имя страницы
        self.name = 'sign_up_page'

        self.grid_columnconfigure((0, 3), weight=1)
        self.grid_rowconfigure((0, 12), weight=1)

        self.register = register_method
        self.login = login_method

        # Заголовок
        self.process_label = ctk.CTkLabel(
            self,
            font=("Arial", 24, "bold"),
            text='Создание аккаунта'
        )

        # Поля ввода и подписи (master теперь self)
        self.name_entry_label = ctk.CTkLabel(
            self,
            text='Отображаемое имя'
        )

        self.name_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            placeholder_text='Например: Всевладеющий'
        )

        self.username_entry_label = ctk.CTkLabel(
            self,
            text='Уникальное имя пользователя'
        )

        self.username_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            placeholder_text='Например: @Nekktor'
        )

        self.password_entry_label = ctk.CTkLabel(
            self,
            text='Придумайте пароль'
        )

        self.password_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            placeholder_text='Пароль'
        )

        self.password_submit_confirm_label = ctk.CTkLabel(
            self,
            text='Подтвердите пароль'
        )

        self.password_confirm_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            placeholder_text='Введите пароль ещё раз'
        )

        # Кнопки
        self.submit_button = ctk.CTkButton(
            self,
            text='Подтвердить',
            width=200, height=45,
            command=self.register
        )

        self.login_button = ctk.CTkButton(
            self,
            text='Войти в аккаунт',
            width=200, height=45,
            fg_color="transparent", border_width=2,
            command=self.show_login_interface
        )

        self.register_button = ctk.CTkButton(
            self,
            text='Зарегистрироваться',
            width=200, height=45,
            fg_color="transparent", border_width=2,
            command=self.show_register_interface
        )

        # Надпись для ошибок
        self.error_label = ctk.CTkLabel(
            self,
            text='',
            text_color="red"
        )

        # Начальное размещение элементов
        self.setup_initial_view()

    def setup_initial_view(self):
        self.process_label.grid(row=1, column=1, columnspan=2, pady=(40, 20))

        self.name_entry_label.grid(row=2, column=1, columnspan=2, pady=(10, 0))
        self.name_entry.grid(row=3, column=1, columnspan=2, pady=10)

        self.username_entry_label.grid(row=4, column=1, columnspan=2, pady=(10, 0))
        self.username_entry.grid(row=5, column=1, columnspan=2, pady=10)

        self.password_entry_label.grid(row=6, column=1, columnspan=2, pady=(10, 0))
        self.password_entry.grid(row=7, column=1, columnspan=2, pady=10)

        self.password_submit_confirm_label.grid(row=8, column=1, columnspan=2, pady=(10, 0))
        self.password_confirm_entry.grid(row=9, column=1, columnspan=2, pady=10)

        # Кнопки тоже можно в сетку, чтобы они не перекрывали текст
        self.login_button.grid(row=10, column=1, pady=20, padx=(0, 10), sticky="w")
        self.submit_button.grid(row=10, column=2, pady=20, padx=(10, 0), sticky="e")

        self.error_label.grid(row=11, column=1, columnspan=2, pady=10)

    def error_callback(self, error):
        self.error_label.configure(text=error)

    def show_login_interface(self):
        # Скрываем лишнее для логина
        self.name_entry_label.grid_remove()
        self.name_entry.grid_remove()
        self.password_submit_confirm_label.grid_remove()
        self.password_confirm_entry.grid_remove()

        # Меняем кнопку переключения
        self.login_button.grid_remove()
        self.register_button.grid(row=10, column=1, pady=20, padx=(0, 10), sticky="w")

        # Настраиваем текст и команды
        self.password_entry_label.configure(text='Пароль')
        self.process_label.configure(text='Вход в аккаунт')
        self.submit_button.configure(command=self.login)
        self.error_label.configure(text='')

    def show_register_interface(self):
        # Возвращаем все элементы на их законные строки
        self.name_entry_label.grid()
        self.name_entry.grid()
        self.password_submit_confirm_label.grid()
        self.password_confirm_entry.grid()

        # Меняем кнопку переключения обратно
        self.register_button.grid_remove()
        self.login_button.grid(row=10, column=1, pady=20, padx=(0, 10), sticky="w")

        # Настраиваем текст и команды
        self.password_entry_label.configure(text='Придумайте пароль')
        self.process_label.configure(text='Создание аккаунта')
        self.submit_button.configure(command=self.register)
        self.error_label.configure(text='')

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()
