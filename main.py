import functools
import json
import time
import inspect
from urllib import response

import websockets
import asyncio
from Database.api import Session, DataBase
import os
from datetime import datetime




class LoggerServer:
    def __init__(self, get_ws_func):
        self.get_ws_func = get_ws_func

    def create_log(self, message, level, duration, inp, response)->str:
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inp = self.del_private_data(inp)
        response = self.del_private_data(response)
        log = f"[LOG]|{level}|{data}|{duration}|{message}|{inp}|{response}"
        return log
    def del_private_data(self, data: str) -> str:
        if isinstance(data, str) and "password" in data:
            l_data = data.split(",")
            for i in range(len(l_data)):
                if "password" in l_data[i]:
                    data = data.replace(l_data[i],"[PRIVATE DATA WAS REMOVED]")

        return data

    async def send_log(self, message, level="DEBUG", duration="?", inp="", response="") -> None:
        ws_list = self.get_ws_func()

        if ws_list:
            for ws in ws_list:
                if ws.open():
                    try:
                        msg = self.create_log(message, level, duration, inp, response)
                        await ws.send(msg)
                    except:
                        pass

    @classmethod
    def auto_log(cls, message="Процесс завершился"):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(server_instance,*args, **kwargs):
                start = time.time()
                res = ""
                lvl = "INFO"
                msg = f" {func.__name__} {message}"
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                inp = ""
                end = 0.0
                for k, v in bound_args.arguments.items():
                    if k != 'self' and k != 'websocket':  # Исключаем служебные параметры
                        inp += f"{k}={v}, "
                try:
                    res = await func(*args, **kwargs)
                    end = time.time()
                    if isinstance(res, str) and "Fall" in res:
                        lvl = "ERROR"
                    return res
                    #проверку на ошибку отслеживаемую
                except Exception as e:
                    end = time.time()
                    res = f"Непредвиденная ошибка: {e}"
                    lvl = "ERROR"
                    raise
                finally:
                    await server_instance.loggerServer.send_log(
                        msg, level=lvl, duration=str(end - start),
                        inp=inp, response=str(res)
                    )

            return wrapper
        return decorator



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
            "auth_for_log": self.auth_for_log,
            "test_method" : self.test_method
        }
        self.PASSWORD_FOR_LOGS = "SuperSlognyiParol"
        self.loggerServer = LoggerServer(get_ws_func=self.get_admins_websockets)
    def get_admins_websockets(self) -> list:
        return self.admins_websockets.copy()


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
                    await self.loggerServer.send_log(message=f"Ошибка: {e}", level="ERROR")
                    print(f"Error: {e}")
        finally:
            user_id = next((userID for userID, ws in self.connected_clients.items() if ws == websocket), None)
            if user_id:
                await websocket.close()
                self.connected_clients.pop(user_id)
            if websocket in self.admins_websockets:
                await websocket.close()
                self.admins_websockets.remove(websocket)


    async def auth_for_log(self, id_task: str, websocket, password: str) -> None:
        try:
            if password == self.PASSWORD_FOR_LOGS:
                self.admins_websockets.append(websocket)
                await websocket.send("Пользователь добавлен")

        except Exception as e:
            await websocket.send("Не удалось добавить пользователя")


    @LoggerServer.auto_log()
    async def registration(self, id_task: str, websocket, name: str, username: str, password: str, lastname: str = ""):
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
        try:
            out = self.db.users.exists(username=username)
            user_id = None
            if out.get("isSuccess") and not out.get("data"):
                out = self.db.users.add(name=name, username=username, password=password, lastname=lastname)
                user_id = out.get("data").get("id")
            else:
                out = {"id_task": id_task, "error": "username уже занят"}
                # out = добавление пользователя в БД, получить словарь или ошибку
            # out = db.users.exists("username", username) # здесь вызвать метода проверки возможности добавления пользователя с пааметрами name, username, lastname (они будут равны = ["Никита2", "Nikitka", "Соколов2"])
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            output = out
            if user_id:  # Проверяем наличие user_id
                self.connected_clients[user_id] = websocket  # Сохраняем клиента по id
            return output
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Error: {e}"}))
            output = json.dumps({"id_task": id_task, "response": f"Error: {e}"})
            return output

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

            output = out
            return output
            #return out
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall: {e}"}))
            output = json.dumps({"id_task": id_task, "response": f"Fall: {e}"})
            return output

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
            out = self.db.messages.add(message_type=message_type, text=text, chat_id=int(chat_id), user_id=user_id)
            users_for_notice = [us.get("id") for us in self.db.select_all_users_by_chat_id(chat_id=int(chat_id))["data"]]
            for user in users_for_notice:
                if user == user_id: continue
                if user in self.connected_clients.keys():
                    await self.give_notifications(id_task="notification", websocket=self.connected_clients[user], text="New message")
            # добавить уведомление пользователям
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            output = out
            return output
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall: {e}"}))
            output = json.dumps({"id_task": id_task, "response": f"Fall {e}"})
            return output

    #@LoggerServer.auto_log()
    async def test_method(self, id_task: str, websocket, arg):
        await websocket.send(json.dumps({"id_task": id_task, "response": arg}))
        await self.loggerServer.send_log(message="Тестовый лог", level="DEBUG", inp=f"{arg}")
        await websocket.send("Лог отправлен")
        return {"response" : "OK"}

    async def get_chats(self, id_task: str, websocket, id_user: str):
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
            output = out
            return output
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall: {e}"}))
            output = json.dumps({"id_task": id_task, "response": f"Fall: {e}"})
            return output

    async def get_messages(self, id_task: str, websocket, chat_id: str):
        """
        Получение данных чата(?)
        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param chat_id: id чата
        """
        try:
            out = self.db.select_recent_messages(chat_id=int(chat_id))
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            output = out
            return output
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall: {e}"}))
            output = json.dumps({"id_task": id_task, "response": f"Fall: {e}"})
            return output

    async def give_notifications(self, id_task: str, websocket, text: str):
        """
        Отправляет уведомления пользователю

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        """
        try:
            await websocket.send(
                json.dumps({"id_task": id_task, "response": text}))
            output = text
            return output
        except Exception as e:
            print(f"Error: {e}")
            output = json.dumps({"id_task": id_task, "response": f"Fall: {e}"})


    async def get_participants(self, id_task: str, websocket, chat_id: str):
        """
        Метод обработки данных чата

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param chat_id: id чата
        """
        try:
            out = self.db.select_chat_participants(chat_id=int(chat_id))

            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            output = out
            return output
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall: {e}"}))
            output = json.dumps({"id_task": id_task, "response": f"Fall: {e}"})
            return output

    async def create_chat(self, id_task: str, websocket, type: str, name: str, avatar_url: str, users_ids: list[str]):
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
                output = json.dumps({"id_task": id_task, "response": "Чат создан"})
                return output
            except Exception as e:
                await websocket.send(json.dumps({"id_task": id_task, "response": f"Не удалось создать чат, Error : {e}"}))
                output = json.dumps({"id_task": id_task, "response": f"Fall: {e}"})
                return output
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall: {e}"}))
            output = json.dumps({"id_task": id_task, "response": f"Fall: {e}"})
            return output

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