import websockets
import asyncio
import datetime
import uuid
import json

url = "ws://localhost:8765"


class TaskManager():
    def __init__(self):
        self.tasks_in_progress = set()  #
        self.queue_tasks = asyncio.Queue()
        self.running = True
        self.id_response = {}

    async def add_task(self, function, id_task, *args):
        # print("add_task")
        self.task_info = {"function": function, "id_task": id_task, "params": args}
        self.current_task = True
        await self.queue_tasks.put(self.task_info)

    async def start_tasks(self, websocket):
        # print("TaskManager запущен")
        await asyncio.gather(self.process_task(),
                             self.get_response(websocket))

    async def process_task(self):
        while self.running:
            print(1)
            # print("1")
            # print(self.queue_tasks)
            task_info = await self.queue_tasks.get()
            # print("2")
            function = task_info["function"]
            id_task = task_info["id_task"]
            params = task_info["params"]
            task = asyncio.create_task(function(id_task, *params))
            # print("3")
            self.tasks_in_progress.add(task)
            task.add_done_callback(lambda x: self.remove_task(x))
            # print("Здача запущена")

    async def get_response(self, websocket):
        async for response in websocket:
            t_response = json.loads(response)
            print(t_response)
            self.id_response[t_response["id_task"]] = t_response["response"]

    def remove_task(self, task):
        if task in self.tasks_in_progress:
            self.tasks_in_progress.remove(task)


# Создание задачи:
# await self.task_manager.add_task(self.methodename, str(uuid.uuid4()), websocket, *input_data)
class Client:
    def __init__(self):
        self.temp_id = str(uuid.uuid4())  # временный id
        self.user_id = ""  # @nickname
        self.task_manager = TaskManager()

    async def connect(self):
        async with websockets.connect(url) as websocket:
            print("Подключено")
            try:
                manager_task = asyncio.create_task(self.task_manager.start_tasks(websocket))
                await asyncio.sleep(0.1)
                user_input = ["Nikitochka"]
                # await self.task_manager.start_tasks(websocket)

                await self.task_manager.add_task(self.auth, str(uuid.uuid4()), websocket, *user_input)
                user_input = [1, 2, "text", "privet", 3]
                await self.task_manager.add_task(self.create_message, str(uuid.uuid4()), websocket, *user_input)
                # print(self.task_manager.current_task)
                print(self.task_manager.id_response)
                await  manager_task
            except Exception as e:
                print(f"Error: {e}")

    async def get_chats(self, id_task, websocket):
        await websocket.send(json.dumps({"action": "get_chats", "id_task": id_task, "params": []}))
        while id_task not in self.task_manager.id_response:
            await asyncio.sleep(0.1)
        if self.task_manager.id_response[id_task] != "Fall":
            return self.task_manager.id_response[id_task]  # возращает чаты
        else:
            print("Не получилось получить чаты")

    async def create_message(self, id_task, websocket, chat_id, user_id, type, text, file_id):
        await websocket.send(json.dumps(
            {"action": "create_message", "id_task": id_task, "params": [chat_id, user_id, type, text, file_id]}))
        while id_task not in self.task_manager.id_response:
            await asyncio.sleep(0.1)

        if self.task_manager.id_response[id_task] != "Fall":
            print("Сообщение отправлено")  # пометка в ui что сообщение отправлено
        else:
            print("Не получилось отправить сообщение")

    async def registration(self, id_task, websocket, name, username, password):
        # print("Отправка")
        await websocket.send(
            json.dumps({"action": "registration", "id_task": id_task, "params": [name, username, password]}))
        while id_task not in self.task_manager.id_response:
            await asyncio.sleep(0.1)

        if self.task_manager.id_response[id_task] == True:
            self.user_id = username
            print("ID (nickname) клиента:", self.user_id)
            return self.task_manager.id_response[id_task]
        else:
            print("Не удалось создать пользователя")

    async def auth(self, id_task, websocket, username, password):
        await websocket.send(json.dumps({"action": "auth", "id_task": id_task, "params": [username, password]}))
        while id_task not in self.task_manager.id_response:
            await asyncio.sleep(0.1)

        if "Error" not in self.task_manager.id_response[id_task]:
            self.user_id = username
            return self.task_manager.id_response[id_task]
        else:
            print("Ошибка")


if __name__ == "__main__":
    client = Client()
    asyncio.run(client.connect())