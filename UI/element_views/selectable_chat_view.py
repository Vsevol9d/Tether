import customtkinter as ctk
from PIL import Image

class SelectableChatView(ctk.CTkFrame):
    def __init__(self, master, avatar_url: str, name: str, last_message: str):
        super().__init__(master, height=60, border_width=1)

        self.pack_propagate(False)

        self.master = master
        self.avatar_url = avatar_url
        self.name = name
        self.last_message = last_message

        self.image = Image.open(self.avatar_url)

        self.avatar_image = ctk.CTkImage(
            dark_image=self.image,
            size=(50, 50)
        )

        self.avatar = ctk.CTkLabel(
            self,
            image=self.avatar_image,
            text=""
        )

        # Отображение имени чата
        self.name_label = ctk.CTkLabel(
            self,
            text=self.name,
            text_color="white",
            font=("Arial", 14)
        )

        max_length = 35
        truncated_message = self.truncate_text(self.last_message, max_length)

        # Отображение последнего сообщения с обрезанным текстом
        self.last_message_label = ctk.CTkLabel(
            self,
            text=truncated_message,
            text_color="gray",
            font=("Arial", 12)
        )

        self.setup_initial_view()

    @staticmethod
    def truncate_text(text: str, max_chars: int) -> str:
        """Обрезает текст и добавляет многоточие, если он длиннее лимита"""
        if len(text) > max_chars:
            return text[:max_chars].strip() + "..."
        return text

    def setup_initial_view(self):
        self.grid_columnconfigure(0, weight=0, minsize=60)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.avatar.grid(column=0, row=0, rowspan=2, pady=5, padx=5, sticky="w")
        self.name_label.grid(column=1, row=0, sticky="sw", pady=5)
        self.last_message_label.grid(column=1, row=1, sticky="nw", pady=5)
