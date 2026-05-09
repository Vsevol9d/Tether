import asyncio
import websockets
import json
from Database.api import Session, DataBase  # Твои импорты БД


class Server():
    def __init__(self):
        self.connected_clients = {}

        # Инициализируем БД здесь или передаем извне
        # Важно: убедись, что Session настроена правильно
        self.db = DataBase(Session())

        self.action_handlers = {
            "registration": self.registration,
            "auth": self.auth,
            "create_message": self.send_message,
            "get_chats": self.get_chats,
            "open_chat": self.open_chat,
            "get_notifications": self.get_notifications
        }
        self.notice = {}

    async def handler(self, websocket):
        """Обрабатывает одного клиента"""
        try:
            print("Клиент подключился")
            # websockets в новых версиях возвращает сообщения по одному
            async for message in websocket:
                t_message = json.loads(message)
                print(f"Получено: {t_message}")

                action = t_message.get("action")
                if action in self.action_handlers:
                    # Вызываем нужный метод.
                    # Внимание: убедись, что методы принимают (id_task, websocket, *params)
                    await self.action_handlers[action](
                        t_message.get("id_task"),
                        websocket,
                        *t_message.get("params", [])
                    )
                else:
                    await websocket.send(json.dumps({"error": f"Unknown action: {action}"}))
        except websockets.exceptions.ConnectionClosed:
            print("Клиент отключился")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            # Удаляем клиента из списка при отключении
            if websocket in self.connected_clients:
                del self.connected_clients[websocket]

    # --- Твои методы (registration, auth и т.д.) ---
    async def registration(self, id_task, websocket, name, username, password):
        try:
            # Используем self.db, который мы создали в __init__
            exists = self.db.users.exists(username=username)
            if not exists:
                out = self.db.users.add(name=name, username=username, password=password)
                await websocket.send(json.dumps({"id_task": id_task, "response": out}))
            else:
                await websocket.send(json.dumps({"id_task": id_task, "response": "User exists"}))
        except Exception as e:
            print(f"Registration Error: {e}")
            await websocket.send(json.dumps({"id_task": id_task, "response": f"Error: {e}"}))

    # Заглушки для остальных методов, чтобы код не падал при запуске
    async def auth(self, *args, **kwargs):
        pass

    async def send_message(self, *args, **kwargs):
        pass

    async def get_chats(self, *args, **kwargs):
        pass

    async def open_chat(self, *args, **kwargs):
        pass

    async def get_notifications(self, *args, **kwargs):
        pass


#  ГЛАВНОЕ: Точка входа для хостинга
async def main():
    server = Server()

    # Запускаем сервер на порту 10000 (требование Render)
    # 0.0.0.0 означает "слушать все сетевые интерфейсы"
    async with websockets.serve(server.handler, "0.0.0.0", 10000):
        print("✅ WebSocket сервер запущен на порту 10000")
        await asyncio.Future()  # Бесконечно ждем событий (loop forever)


if __name__ == "__main__":
    asyncio.run(main())