# server_api.py
import asyncio
import json
import uuid
import websockets


class ServerAPI:
    def __init__(self):
        self.websocket = None
        self.connected = False
        self._response_futures = {}
        self._listen_task = None

    async def connect(self, url: str = "wss://tether-jj4v.onrender.com/ws"):
        """Установка соединения с сервером"""
        self.websocket = await websockets.connect(url)
        self.connected = True
        self._listen_task = asyncio.create_task(self._listen_responses())
        return self

    async def _listen_responses(self):
        """Слушает ответы от сервера"""
        try:
            async for response in self.websocket:
                data = json.loads(response)
                task_id = data.get("id_task")
                if task_id and task_id in self._response_futures:
                    future = self._response_futures.pop(task_id)
                    if not future.done():
                        future.set_result(data.get("response"))
        except websockets.exceptions.ConnectionClosed:
            self.connected = False

    async def _send_request(self, action: str, params: list):
        """Отправляет запрос и ждет ответа"""
        task_id = str(uuid.uuid4())
        future = asyncio.Future()
        self._response_futures[task_id] = future

        await self.websocket.send(json.dumps({
            "action": action,
            "id_task": task_id,
            "params": params
        }))

        return await asyncio.wait_for(future, timeout=30.0)

    # ============ API МЕТОДЫ ============

    async def register_user(self, name: str, username: str, password: str):
        """Регистрация пользователя"""
        return await self._send_request("registration", [name, username, password])

    async def login_user(self, username: str, password: str):
        """Авторизация пользователя"""
        return await self._send_request("auth", [username, password])

    async def get_user_chats(self, user_id: str):
        """Получение всех чатов пользователя"""
        return await self._send_request("get_chats", [user_id])

    async def get_messages(self, chat_id: str):
        """Получение сообщений чата"""
        return await self._send_request("get_messages", [chat_id])

    async def send_message(self, message_type: str, text: str, chat_id: str, user_id: str):
        """Отправка сообщения"""
        return await self._send_request("create_message", [message_type, text, chat_id, user_id])

    async def get_notifications(self, user_id: str):
        """Получение уведомлений"""
        return await self._send_request("get_notifications", [user_id])

    async def get_chat_data(self, chat_id: str):
        """Получение информации о чате"""
        return await self._send_request("get_chat_data", [chat_id])

    async def create_chat(self, chat_type: str, name: str, avatar_url: str):
        """Создание чата (без участников)"""
        return await self._send_request("create_chat", [chat_type, name, avatar_url])

    async def close(self):
        """Закрытие соединения"""
        self.connected = False
        if self._listen_task:
            self._listen_task.cancel()
        if self.websocket:
            await self.websocket.close()