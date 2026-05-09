import json
import websockets
import asyncio
from Database.api import Session, DataBase
import os

class Server():
    def __init__(self):
        """
        connected_clients - словарь {id_user : websocket}
        action_handlers - типы запросов от клиентов и вызов в зависимости от этого функцию
        notice - словарь {user_id : список сообщений-уведомлений}
        """

        self.connected_clients = {}
        self.db = DataBase(Session())
        # self.clients = set()

        self.action_handlers = {
            "registration": self.registration,
            "auth": self.auth,
            "create_message": self.send_message,
            "get_chats": self.get_chats,
            "open_chat": self.open_chat,
            "get_notifications": self.give_notifications
        }

        self.notice = {}  # user_id : notice[textNotice]

    async def handler(self, websocket) -> None:
        """
        Функция связи с отдельным пользователем
        :param websocket: объект - соединение с пользователем(не для заполнения аргумент)

        Экземпляр функции создается для КАЖДОГО отдельного клиента
        """
        try:
            print("Подключено")
            async for message in websocket:
                t_message = json.loads(message)
                print(f"1 + {t_message}")
                await self.action_handlers[t_message["action"]](t_message["id_task"], websocket, *t_message["params"])
        finally:
            for c in self.connected_clients:
                if self.connected_clients[c] == websocket:
                    self.connected_clients[c].close()

    async def registration(self, id_task: str, websocket, name: str, username: str, password: str) -> None:
        """
        Функция регистрации пользователя в БД

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param name: имя пользователя
        :param username: username пользователя(уникальное имя)
        :param password: пароль
        """
        try:
            out = self.db.users.exists("username", username)
            if not out:
                out = self.db.users.add(name=name, username=username, password=password)
                # out = добавление пользователя в БД, получить словарь или ошибку
            # out = db.users.exists("username", username) # здесь вызвать метода проверки возможности добавления пользователя с пааметрами name, username, lastname (они будут равны = ["Никита2", "Nikitka", "Соколов2"])
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Error: {e}"}))

    async def auth(self, id_task: str, websocket, username: str, password: str) -> None:
        """
        Функция авторизации пользователя

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param username: username пользователя(уникальное имя)
        :param password: пароль
        """
        try:
            # проверка на свопадения пароля с паролем username out = db.users.exists("username", username)

            out = self.db.users.exists(username=username, password=password)
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            self.connected_clients[username] = websocket
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall"}))

    async def send_message(self, id_task: str, websocket, message_type: str, text: str, chat_id: str, user_id: str):
        """
        Функция отправки сообщения

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param message_type: тип сообщения(text, image и другие)
        :param text: содержимое сообщения(тип - text)
        :param chat_id: id чата, куда отправляется сообщение
        :param user_id: id пользователя, который отправил сообщение
        """
        try:
            out = self.db.messages.add(message_type=message_type, text=text, chat_id=chat_id, user_id=user_id)

            # добавить уведомление пользователям
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def get_chats(self, id_task: str, websocket) -> None:
        """
        Получение всех чатов

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        """
        try:
            chats = {}  # чаты из БД
            await websocket.send(json.dumps({"id_task": id_task, "response": chats}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def open_chat(self, id_task: str, websocket, user_id: str) -> None:
        """
        Получение данных чата(?)
        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param user_id: id пользователя
        """
        try:
            out = self.db.users.exists("")
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    def add_notice(self, user_id: str, text: str) -> None:
        """
        Добавляет уведомление в список уведомлений на отправку

        :param user_id: id пользователя
        :param text: текст уведомления
        """
        if user_id not in self.notice:
            self.notice[user_id] = []

        self.notice[user_id].append(text)

    async def give_notifications(self, id_task: str, websocket, user_id: str) -> None:
        """
        Отправляет уведомления пользователю

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param user_id: id пользователя
        """

        await websocket.send(
            json.dumps({"id_task": id_task, "response": self.notice[user_id]}))

    async def start_server(self) -> None:
        port = int(os.environ.get("PORT", 5000))
        async with websockets.serve(self.handler, "localhost", port):
            print("Server started")
            await asyncio.Future()


server = Server()
asyncio.run(server.start_server())
"""if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start_server())"""