# client_ws.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import websocket

SERVER_WS = "wss://tether-jj4v.onrender.com/ws"  # Для Render: wss://tether-jj4v.onrender.com/ws
# SERVER_HTTP = "http://127.0.0.1:8000"  # Для HTTP-запросов


class TetherClient:
    def __init__(self, root):
        self.root = root
        self.ws = None
        self.user_id = None

        self._setup_ui()

    def _setup_ui(self):
        self.root.title("Tether Messenger")
        self.root.geometry("500x400")

        # 🔹 Панель логина
        self.frame_login = ttk.Frame(self.root, padding=10)
        self.frame_login.pack(fill="x")

        ttk.Label(self.frame_login, text="Ваш ID:").pack(side="left")
        self.entry_user_id = ttk.Entry(self.frame_login, width=15)
        self.entry_user_id.pack(side="left", padx=5)
        self.entry_user_id.insert(0, "Nikita")

        ttk.Button(self.frame_login, text="Подключиться",
                   command=self._connect_ws).pack(side="left", padx=10)

        # 🔹 Панель чата
        self.frame_chat = ttk.Frame(self.root, padding=10)
        self.frame_chat.pack(fill="both", expand=True)

        self.text_chat = tk.Text(self.frame_chat, height=15, state="disabled")
        self.text_chat.pack(fill="both", expand=True)

        self.frame_input = ttk.Frame(self.frame_chat)
        self.frame_input.pack(fill="x", pady=5)

        self.entry_message = ttk.Entry(self.frame_input)
        self.entry_message.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_message.bind("<Return>", lambda e: self._send_message())

        ttk.Button(self.frame_input, text="Отправить",
                   command=self._send_message).pack(side="right")

        # 🔹 Статус
        self.label_status = ttk.Label(self.root, text="❌ Отключён", foreground="red")
        self.label_status.pack(pady=5)

    def _connect_ws(self):
        """Подключается к WebSocket"""
        self.user_id = self.entry_user_id.get().strip()
        if not self.user_id:
            messagebox.showwarning("ID", "Введите ваш ID")
            return

        # 🔹 Запускаем WebSocket в отдельном потоке
        ws_url = f"{SERVER_WS}/{self.user_id}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_ws_open,
            on_message=self._on_ws_message,
            on_error=self._on_ws_error,
            on_close=self._on_ws_close
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def _on_ws_open(self, ws):
        """Вызывается при успешном подключении"""
        self.root.after(0, lambda: self.label_status.config(
            text="✅ Подключён", foreground="green"))
        self._log_system("Подключено к серверу")

    def _on_ws_message(self, ws, message):
        """Обработка входящих сообщений"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "new_message":
                # Новое сообщение от другого пользователя
                self.root.after(0, lambda: self._log_message(
                    f"{data['from']}: {data['text']}"))
            elif msg_type == "message_sent":
                # Подтверждение отправки
                self.root.after(0, lambda: self._log_system("✓ Сообщение доставлено"))
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")

    def _on_ws_error(self, ws, error):
        self.root.after(0, lambda: self._log_system(f"Ошибка: {error}"))

    def _on_ws_close(self, ws, close_status_code, close_msg):
        self.root.after(0, lambda: self.label_status.config(
            text="❌ Отключён", foreground="red"))

    def _send_message(self):
        """Отправляет сообщение через WebSocket"""
        text = self.entry_message.get().strip()
        if not text or not self.ws or not self.user_id:
            return

        message = {
            "type": "chat_message",
            "to": "Friend",  # 🔹 В реальном проекте: выбор получателя
            "text": text,
            "timestamp": "2026-05-09T12:00:00"  # 🔹 Используй datetime.now().isoformat()
        }

        self.ws.send(json.dumps(message))
        self.entry_message.delete(0, "end")
        self._log_message(f"Вы: {text}")

    def _log_message(self, text: str):
        """Добавляет сообщение в чат"""
        self.text_chat.config(state="normal")
        self.text_chat.insert("end", text + "\n")
        self.text_chat.see("end")
        self.text_chat.config(state="disabled")

    def _log_system(self, text: str):
        """Добавляет системное сообщение"""
        self.text_chat.config(state="normal")
        self.text_chat.insert("end", f"⚙️ {text}\n", "system")
        self.text_chat.see("end")
        self.text_chat.config(state="disabled")
        self.text_chat.tag_config("system", foreground="gray")


# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = TetherClient(root)
    root.mainloop()