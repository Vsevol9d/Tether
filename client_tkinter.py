# client_tkinter.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

SERVER_URL = "https://tether-jj4v.onrender.com"  # На Render (сервер в интернете)
# SERVER_URL = "http://127.0.0.1:8000" # Локально

def check_user_on_server(username: str) -> dict:
    """Отправляет запрос на сервер и возвращает ответ"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/check-user",
            json={"command": "exists", "username": username},
            timeout=10  # Ждём не дольше 10 секунд
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка сети: {e}"}


def on_check_click():
    """Обработчик кнопки (запускается в отдельном потоке)"""
    username = entry_username.get().strip()
    if not username:
        messagebox.showwarning("Ввод", "Введите имя пользователя")
        return

    # 🔹 Блокируем интерфейс на время запроса
    btn_check.config(state="disabled")
    label_result.config(text="🔄 Запрос к серверу...", foreground="blue")

    # 🔹 Запускаем запрос в отдельном потоке, чтобы UI не завис
    def background_task():
        result = check_user_on_server(username)
        print(result)
        # 🔹 Возвращаемся в главный поток для обновления UI
        root.after(0, lambda: update_ui(result))

    threading.Thread(target=background_task, daemon=True).start()


def update_ui(result: dict):
    """Обновляет интерфейс с результатом (вызывается в главном потоке)"""
    btn_check.config(state="normal")  # Разблокируем кнопку

    if "error" in result:
        label_result.config(text=f"❌ {result['error']}\nПопробуйте ещё раз", foreground="red")
        messagebox.showerror("Ошибка", result["error"])
    else:
        status_icon = "✅ ошибок нет\n" if result.get("isSuccess") else "❌"
        color = "green" if result.get("isSuccess") else "orange"
        ans = 'Такой пользователь есть' if result.get('data') else 'Такого пользователя нет'
        label_result.config(text=f"{status_icon} {ans}", foreground=color)


# 🔹 Создаём окно
root = tk.Tk()
root.title("Tether Client")
root.geometry("400x250")
root.resizable(False, False)

# 🔹 Элементы интерфейса
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

# 🔹 Обработка Enter в поле ввода
entry_username.bind("<Return>", lambda e: on_check_click())

# 🔹 Запуск
root.mainloop()