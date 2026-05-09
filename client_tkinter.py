# client_tkinter.py
import tkinter as tk
from tkinter import ttk, messagebox
import websocket  # ← Новая библиотека
import json
import threading
import time

# 🔹 Адрес сервера (WebSocket)
# Для Render: wss:// (безопасный)
# Для локального: ws://
SERVER_WS = "wss://tether-jj4v.onrender.com"


# SERVER_WS = "ws://127.0.0.1:10000"  # Локальный тест

def check_user_on_server(username: str) -> dict:
    """Отправляет запрос через WebSocket и возвращает ответ"""

    message = {
        "action": "registration",
        "id_task": "check_user_" + str(time.time()),
        "params": [username, username, "temp_password"]  # name, username, password
    }

    result_container = {"response": None, "error": None}

    def on_message(ws, msg):
        try:
            data = json.loads(msg)
            if data.get("id_task") == message["id_task"]:
                result_container["response"] = data.get("response")
                ws.close()
        except Exception as e:
            result_container["error"] = f"Ошибка парсинга: {e}"
            ws.close()

    def on_error(ws, error):
        result_container["error"] = f"WebSocket error: {error}"

    def on_close(ws, close_status_code, close_msg):
        pass

    def on_open(ws):
        ws.send(json.dumps(message))

    try:
        ws = websocket.WebSocketApp(
            SERVER_WS,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever(ping_timeout=10)

        if result_container["error"]:
            return {"error": result_container["error"]}
        elif result_container["response"] is not None:
            response = result_container["response"]
            if isinstance(response, dict):
                return response
            else:
                return {"isSuccess": True, "data": response}
        else:
            return {"error": "Нет ответа от сервера"}
    except Exception as e:
        return {"error": f"Ошибка подключения: {e}"}


def on_check_click():
    """Обработчик кнопки (запускается в отдельном потоке)"""
    username = entry_username.get().strip()
    if not username:
        messagebox.showwarning("Ввод", "Введите имя пользователя")
        return

    btn_check.config(state="disabled")
    label_result.config(text="🔄 Запрос к серверу...", foreground="blue")

    def background_task():
        result = check_user_on_server(username)
        print(result)
        root.after(0, lambda: update_ui(result))

    threading.Thread(target=background_task, daemon=True).start()


def update_ui(result: dict):
    """Обновляет интерфейс с результатом (вызывается в главном потоке)"""
    btn_check.config(state="normal")

    if "error" in result:
        label_result.config(text=f"❌ {result['error']}\nПопробуйте ещё раз", foreground="red")
        messagebox.showerror("Ошибка", result["error"])
    else:
        status_icon = "✅ ошибок нет\n" if result.get("isSuccess") else "❌"
        color = "green" if result.get("isSuccess") else "orange"
        ans = 'Такой пользователь есть' if result.get('data') else 'Такого пользователя нет'
        label_result.config(text=f"{status_icon} {ans}", foreground=color)


# 🔹 Создаём окно (без изменений!)
root = tk.Tk()
root.title("Tether Client")
root.geometry("400x250")
root.resizable(False, False)

ttk.Label(root, text="Проверка пользователя", font=("Arial", 14, "bold")).pack(pady=10)

frame_input = ttk.Frame(root)
frame_input.pack(pady=5)

ttk.Label(frame_input, text="Username пользователя:").pack(side="left", padx=5)
entry_username = ttk.Entry(frame_input, width=20)
entry_username.pack(side="left", padx=5)
entry_username.focus()

btn_check = ttk.Button(root, text="Проверить", command=on_check_click)
btn_check.pack(pady=10)

label_result = ttk.Label(root, text="", font=("Arial", 10))
label_result.pack(pady=10)

entry_username.bind("<Return>", lambda e: on_check_click())

root.mainloop()