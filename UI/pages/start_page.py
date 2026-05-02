import customtkinter as ctk

class StartPage(ctk.CTkFrame):
    def __init__(self, master):
        # Инициализируем сам класс как CTkFrame
        super().__init__(master, corner_radius=0)

        # Имя страницы
        self.name = 'start_page'

        # Элементы стартовой страницы
        # Теперь master для label — это self (сам фрейм страницы)
        self.welcome_label = ctk.CTkLabel(
            self,
            text="Welcome to Communicator!",
            font=("Arial", 32, "bold")
        )

        # Центрируем надпись
        self.welcome_label.pack(expand=True)

    def show(self):
        # Показываем саму страницу
        self.pack(fill="both", expand=True)

    def hide(self):
        # Скрываем саму страницу
        self.pack_forget()
