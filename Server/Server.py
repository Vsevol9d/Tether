import json

import websockets
import asyncio
from Database.api import Session, DataBase


class Server():
    def __init__(self):
        self.connected_clients = {}
        self.clients = set()

        self.action_handlers = {
            "registration" : self.registration,
            "auth" : self.auth,
            "create_message" : self.create_message,
            "get_chats" : self.get_chats,
            "open_chat" : self.open_chat
        }

    async def handler(self, websocket):
        try:
            print("Подключено")
            async for message in websocket:

                t_message = json.loads(message)
                print(f"1 + {t_message}")
                await self.action_handlers[t_message["action"]](t_message["id_task"], websocket,  *t_message["params"])
        finally:
            for c in self.connected_clients:
                c.close()

    async def registration(self, id_task, websocket, name, username, password):
        try:
            out = db.users.exists("username", username)
            if not out:
                out = db.users.add(name=name, username=username, password=password)
                #out = добавление пользователя в БД, получить словарь или ошибку
                pass
            #out = db.users.exists("username", username) # здесь вызвать метода проверки возможности добавления пользователя с пааметрами name, username, lastname (они будут равны = ["Никита2", "Nikitka", "Соколов2"])
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Error: {e}"}))

    async def auth(self, id_task, websocket, username, password):
        try:
            # проверка на свопадения пароля с паролем username out = db.users.exists("username", username)

            out = db.users.exists(username=username, password=password)
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            self.connected_clients[username] = websocket
            self.clients.add(websocket)
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Fall"}))

    async def send_message(self, id_task, websocket, message_type, text, chat_id, user_id):
        try:
            out = db.messages.add(message_type=message_type, text=text, chat_id=chat_id, user_id=user_id)

            #создание сообщения, добавлен е его в чат БД
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def get_chats(self, id_task, websocket):
        try:
            chats = {}#чаты из БД
            await websocket.send(json.dumps({"id_task": id_task, "response" : chats}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))

    async def open_chat(self, id_task, websocket, user_id):
        try:
            out = db.users.exists("")
            await websocket.send(json.dumps({"id_task": id_task, "response": out}))
        except Exception as e:
            print(f"Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": "Fall"}))



    async def start_server(self):
        async with websockets.serve(self.handler, "localhost", 8765):
            print("Server started")
            await asyncio.Future()




with Session() as session:
    db = DataBase(session)
    try:
        with session.begin():  # ← одна транзакция на всё
                # РАБОЧАЯ ЧАСТЬ
                #db.users.exists("username")
                if __name__ == "__main__":
                    server = Server()
                    asyncio.run(server.start_server())
    except Exception as e:
        print(f"Ошибка: {e}")

"""if __name__ == "__main__":
    server = Server()
    asyncio.run(server.start_server())"""