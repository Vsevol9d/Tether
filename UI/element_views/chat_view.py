import customtkinter as ctk

#----------------------# Вид чата #-------------------------

class ChatView(ctk.CTkFrame):
    def __init__(self, master, chat_type: str, name: str, participants_count: int, avatar_url: str, send_message, see_chat_info):
        super().__init__(master, corner_radius=0, border_width=1, border_color="gray", fg_color="#696969")

        self.chat_type = chat_type
        self.name = name
        self.participants_count = participants_count
        self.avatar_url = avatar_url
        self.send_message = send_message
        self.see_chat_info = see_chat_info

        self.grid_propagate(False)

#---------------------------# Верхняя панель #--------------------------

        self.chat_tool_panel_frame = ctk.CTkFrame(
            self,
            height=50,
            corner_radius=0,
            border_width=1,
            border_color="gray"
        )
        self.chat_tool_panel_frame.grid_propagate(False)

        self.chat_name_label = ctk.CTkLabel(
            self.chat_tool_panel_frame,
            text=self.name,
            font=("Arial", 14, 'bold')
        )

        if participants_count != 2:
            if participants_count % 10 < 5 and participants_count // 10 != 1:
                self.ending = 'а'
            else:
                self.ending = 'ов'

            self.participants_count_label = ctk.CTkLabel(
                self.chat_tool_panel_frame,
                text=str(self.participants_count) + ' участник' + self.ending,
                font=("Arial", 12)
            )

        self.chat_tool_panel_frame.bind('<Button-1>', self.see_chat_info)

#-----------------------------------------------------------------------

        self.messages_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#696969"
        )

        # Поле для ввода сообщения на отправку
        self.message_entry = ctk.CTkEntry(
            self,
            height=40,
            placeholder_text='Сообщение'
        )
        self.message_entry.grid_propagate(False)

        self.send_button = ctk.CTkButton(
            self,
            height=40,
            width=40,
            text='',
            corner_radius=20,
            command=self.send_message
        )
        self.send_button.grid_propagate(False)

######### --- Надпись нового чата (без сообщений) --- #########

        self.begin_chatting_label = ctk.CTkLabel(
            self.messages_frame,
            font=("Arial", 12),
            fg_color="#2E2E2E",
            corner_radius=5,
            text='Начните общение!'
        )

        self.setup_initial_view()

    def setup_initial_view(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure((0, 2), weight=0)
        self.rowconfigure(1, weight=1)

        if self.chat_type == 'group':
            self.chat_tool_panel_frame.grid(column=0, row=0, sticky='nsew', columnspan=2)

            self.chat_tool_panel_frame.columnconfigure(0, weight=1)
            self.chat_tool_panel_frame.rowconfigure((0, 1), weight=1)

            self.chat_name_label.grid(column=0, row=0, sticky='w', padx=5, pady=5)
            self.participants_count_label.grid(column=0, row=1, sticky='w', padx=5, pady=5)

        self.messages_frame.grid(column=0, row=1, sticky='nsew', columnspan=2)
        self.message_entry.grid(column=0, row=2, sticky='nsew', padx=5, pady=5)
        self.send_button.grid(column=1, row=2, sticky='nsew', padx=5, pady=5)

    def on_new_chat_selection(self):
        self.begin_chatting_label.place(relx=0.5, rely=0.5, anchor="center")

    def on_first_message_sending(self):
        self.begin_chatting_label.destroy()

##############################################################################################
# Вид сообщения
##############################################################################################

class MessageView(ctk.CTkFrame):
    def __init__(self, master, content_type: str, content: str, sender: str):
        super().__init__(master, corner_radius=15, border_width=1, border_color="gray")

        self.type = content_type
        self.content = content
        self.sender = sender

        # Label для имени отправителя
        self.sender_label = ctk.CTkLabel(self, text=self.sender, font=("Arial", 12), text_color="#20B2AA")

        # Label для текста сообщения
        self.content_label = ctk.CTkLabel(self, text=self.content, font=("Arial", 14))

        self.setup_initial_view()

    def setup_initial_view(self):
        self.sender_label.pack(side='top', anchor='ne', pady=(5, 0), padx=10)
        self.content_label.pack(side='top', anchor='sw', pady=(0, 5), padx=10)

##############################################################################################
# Вывод информации о чате
##############################################################################################

class ChatInfoView(ctk.CTkToplevel):
    def __init__(self, master, current_chat, participants_names: list):
        super().__init__(master, width=200, height=400)
        self.title("О чате")

        self.current_chat = current_chat

        self.chat_name = current_chat.name
        self.participants_names = participants_names
        self.participants_count = len(self.participants_names)

        self.name_label = ctk.CTkLabel(
            self,
            font=("Arial", 16, 'bold'),
            text=self.chat_name
        )

        self.participants_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=5,
            label_text=f'Участники ({self.participants_count}):'
        )

        for participant in participants_names:
            participant_label = ctk.CTkLabel(
                self.participants_frame,
                text=participant,
                font=("Arial", 14)
            )
            participant_label.pack(side='top', anchor='nw', padx=5, pady=5)

        self.setup_initial_view()

        self.bind("<FocusOut>", lambda event: self.on_focus_lost(event))

    def on_focus_lost(self, event):
        if event.widget == self:
                self.destroy()

    def setup_initial_view(self):
        self.grid_rowconfigure(1, weight=1)

        self.name_label.grid(column=0, row=0, sticky='n', pady=10)
        self.participants_frame.grid(column=0, row=1, sticky='nsew')