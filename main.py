import json
import sys

import websockets
import asyncio
from Database.api import Session, DataBase
import os
import logging
import logging.config, logging.handlers

class CustomWebSocketHandler(logging.Handler):
    def __init__(self, get_ws_func):
        super().__init__()
        self.get_ws_func = get_ws_func

    def emit(self, record):
        ws_list = self.get_ws_func()()
        for websocket in ws_list:
            try:
                asyncio.create_task(self.safe_send(self.format(record), websocket))
            except Exception as e:
                print(e)
    async def safe_send(self, message, websocket):
        if websocket.open:
            await websocket.send(f"[LOG] {message}")

class LoggerServer():
    def __init__(self, get_ws_func):
        self.LOG_CONFIG = {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
                },
                "input_response": {
                    "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s, input: %(input)s, response: %(response)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "input_response",
                }
            },
            "loggers": {
                "server": {
                    "handlers": ["console"],
                    "level": "DEBUG",
                    "propagate": False,
                }
            }
        }
        logging.config.dictConfig(self.LOG_CONFIG)
        self.logger = logging.getLogger("server")
        if websockets:
            ws_handler = CustomWebSocketHandler(get_ws_func)
            ws_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s, input: %(input)s, response: %(response)s")
            ws_handler.setFormatter(formatter)
            self.logger.addHandler(ws_handler)

    def debug(self, message, **extra):
        self.logger.debug(message, extra=extra)

    def info(self, message, **extra):
        self.logger.info(message, extra=extra)

    def warning(self, message, **extra):
        self.logger.warning(message, extra=extra)

    def error(self, message, **extra):
        self.logger.error(message, extra=extra)

    def critical(self, message, **extra):
        self.logger.critical(message, extra=extra)

class Server():
    def __init__(self):
        """
        connected_clients - словарь {id_user : websocket}
        action_handlers - типы запросов от клиентов и вызов в зависимости от этого функцию
        notice - словарь {user_id : список сообщений-уведомлений}
        """

        self.connected_clients = {}
        self.db = DataBase(Session())
        self.admins_websockets = []

        self.action_handlers = {
            "registration": self.registration,
            "auth": self.auth,
            "create_message": self.send_message,
            "get_chats": self.get_chats,
            "get_messages": self.get_messages,
            "get_notifications": self.give_notifications,
            "get_participants" : self.get_participants,
            "create_chat" : self.create_chat,
            "auth_for_log": self.auth_for_log
        }
        self.loggerForServer = LoggerServer(get_ws_func=self.get_admins_websockets)
        self.PASSWORD_FOR_LOGS = "SuperSlognyiParol"
    def get_admins_websockets(self) -> list:
        return self.admins_websockets.copy()



    def send_log(self, message, level, inp, response):
        inp = self.del_private_data(inp)
        match level:
            case "DEBUG":
                self.loggerForServer.debug(message=message, input=inp, response=response)
            case "INFO":
                self.loggerForServer.info(message=message, input=inp, response=response)
            case "WARNING":
                self.loggerForServer.warning(message=message, input=inp, response=response)
            case "ERROR":
                self.loggerForServer.error(message=message, input=inp, response=response)
            case "CRITICAL":
                self.loggerForServer.critical(message=message, input=inp, response=response)

    def del_private_data(self, data: str) -> str:
        if isinstance(data, str) and "password" in data.lower():
            list_data = data.split(",")
            for i in range(len(list_data)):
                if list_data[i] == "password":
                    data = data.replace(list_data[i+1], "[PRIVATE DATA WAS REMOVED]")

        return data

    async def handler(self, websocket) -> None:
        """
        Функция связи с отдельным пользователем
        :param websocket: объект - соединение с пользователем(не для заполнения аргумент)

        Экземпляр функции создается для КАЖДОГО отдельного клиента
        """
        try:
            print("Подключено")
            async for message in websocket:
                try:
                    t_message = json.loads(message)
                    print(f"1 + {t_message}")
                    await self.action_handlers[t_message["action"]](t_message["id_task"], websocket, *t_message["params"])
                except Exception as e:
                    print(f"Error: {e}")
        finally:
            user_id = next((userID for userID, ws in self.connected_clients.items() if ws == websocket), None)
            if user_id:
                websocket.close()
                self.connected_clients.pop(user_id)
            if websocket in self.admins_websockets:
                websocket.close()
                self.admins_websockets.remove(websocket)


    async def auth_for_log(self, id_task: str, websocket, password: str) -> None:
        try:
            if password == self.PASSWORD_FOR_LOGS:
                self.admins_websockets.append(websocket)
            await websocket.send("Пользователь добавлен")
        except Exception as e:
            await websocket.send("Не удалось добавить пользователя")

        await asyncio.sleep(5)
        await websocket.send("Отправили лог" + str(websocket))
        self.send_log("Тестовый лог", level="DEBUG", inp=f"{id_task=}, {password=}", response="None")


    async def registration(self, id_task: str, websocket, name: str, username: str, password: str, lastname: str = "") -> None:
        """
        Функция регистрации пользователя в БД

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param name: имя пользователя
        :param username: username пользователя(уникальное имя)
        :param password: пароль
        :param lastname: фамилия
        """
        print("Регистрируемся")
        self.send_log(message="Регистрируемся", level="DEBUG", inp=f"{id_task=}, {name=}, {username=}, {password=}, {lastname=}", response="Нема")
        try:
            out = self.db.users.exists(username=username)
            user_id = None
            if out.get("isSuccess") and out.get("data"):
                out = self.db.users.add(name=name, username=username, password=password, lastname=lastname)
                user_id = out.get("data").get("id")
                # out = добавление пользователя в БД, получить словарь или ошибку
            # out = db.users.exists("username", username) # здесь вызвать метода проверки возможности добавления пользователя с пааметрами name, username, lastname (они будут равны = ["Никита2", "Nikitka", "Соколов2"])
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            if user_id:  # Проверяем наличие user_id
                self.connected_clients[user_id] = websocket  # Сохраняем клиента по id
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Error: {e}"}))

    async def auth(self, id_task: str, websocket, username: str, password: str):
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
            # Пример из Server.auth
            user_id = None
            if out.get("isSuccess"):
                out = self.db.select_user_by_username(username=username)
                user_id = out.get("data").get("id")  # Получаем id пользователя

            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            if user_id:  # Проверяем наличие user_id
                self.connected_clients[user_id] = websocket  # Сохраняем клиента по id
            #return out
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall"}))

    async def send_message(self, id_task: str, websocket, message_type: str, text: str, chat_id: str, user_id: str) -> None:
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
            out = self.db.messages.add(message_type=message_type, text=text, chat_id=int(chat_id), user_id=user_id)
            users_for_notice = [us.get("id") for us in self.db.select_all_users_by_chat_id(chat_id=int(chat_id))["data"]]
            for user in users_for_notice:
                if user == user_id: continue
                if user in self.connected_clients.keys():
                    await self.give_notifications(id_task="notification", websocket=self.connected_clients[user], text="New message")
            # добавить уведомление пользователям
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def get_chats(self, id_task: str, websocket, id_user: str) -> None:
        """
        Получение всех чатов

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param id_user: id пользователя
        """
        try:
            #out = self.db.select_all_chats_by_id_user(user_id=int(id_user))  # чаты из БД
            out = self.db.select_chats(user_id=int(id_user))
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def get_messages(self, id_task: str, websocket, chat_id: str) -> None:
        """
        Получение данных чата(?)
        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param chat_id: id чата
        """
        try:
            out = self.db.select_recent_messages(chat_id=int(chat_id))
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def give_notifications(self, id_task: str, websocket, text: str) -> None:
        """
        Отправляет уведомления пользователю

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        """
        try:
            await websocket.send(
                json.dumps({"id_task": id_task, "response": text}))
        except Exception as e:
            print(f"Error: {e}")

    async def get_participants(self, id_task: str, websocket, chat_id: str) -> None:
        """
        Метод обработки данных чата

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param chat_id: id чата
        """
        try:
            out = self.db.select_chat_participants(chat_id=int(chat_id))

            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def create_chat(self, id_task: str, websocket, type: str, name: str, avatar_url: str, users_ids: list[str]) -> None:
        """
        Создание чата

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param type: тип чата
        :param name: имя чата
        :param avatar_url: ссылка на изображение автара чата
        :param users_ids: список id пользоовтаелей чата
        """
        try:
            out = self.db.chats.add(type=type, name=name, avatar_url=avatar_url)
            chat_id = out["data"]["id"]
            users_for_notice = [us.get("id") for us in self.db.select_all_users_by_chat_id(chat_id=int(chat_id))["data"]]
            try:
                for uid in users_ids:
                    if self.connected_clients.get(uid) != websocket:
                        self.db.participants.add(user_id=int(uid), chat_id=int(chat_id), role="Участник")

                for user in users_for_notice:
                    if user in self.connected_clients.keys():
                        await self.give_notifications(id_task="notification", websocket=self.connected_clients[user], text="You was added in chat")
            except Exception as e:
                await websocket.send(json.dumps({"id_task": id_task, "response": f"Не удалось создать чат, Error : {e}"}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def start_server(self) -> None:
        port = int(os.environ.get("PORT", 5000))
        async with websockets.serve(self.handler,
                                    "0.0.0.0",
                                    port,
                                    compression=None,
                                    ping_interval=20,
                                    ping_timeout=60,
                                    close_timeout=10):
            print("Server started")
            await asyncio.Future()


server = Server()
asyncio.run(server.start_server())
"""if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start_server())"""