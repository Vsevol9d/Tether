
import websockets
import asyncio
import datetime
import uuid
import json


url = "wss://tether-jj4v.onrender.com/ws" #ссылка на сервер

name = "seva"
username = "seva23"
password = "1234"
class TaskManager():
    def __init__(self):
        """
        task_in_progress - задачи в процессе
        queue_tasks - очередь еще не выполняющихся задач
        running - запущен ли TaskManager
        id_response - словарь {id_task : response}
        """

        self.tasks_in_progress = set()  #
        self.queue_tasks = asyncio.Queue()
        self.running = True
        self.id_response = {}

    async def add_task(self, function, id_task: str, websocket, *args, timeout=None) -> asyncio.Future:
        # print("add_task")
        """
        Создание задачи и ожидания ответа на неё
        :param function: функция, которая делается задачей
        :param id_task: id задачи
        :param websocket: объект-соединение с пользователем
        :param args: входные данные функции
        :param timeout: время ожидания в секундах
        :return: сначало asyncio.Future() - заглушка для реального ответа,
        когда ответ появился, future становится ответом и возвращается результат в основной код
        """
        future = asyncio.Future()
        self.id_response[id_task] = future
        print(f"Результат задачи{id_task} = {self.id_response[id_task]}")

        self.task_info = {"function": function,
                          "id_task": id_task,
                          "websocket" : websocket,
                          "params": args,
                          "timeout" : timeout}
        self.current_task = True
        await self.queue_tasks.put(self.task_info)
        print("future:", future)
        return await future


    async def start_tasks(self, websocket) -> None:
        """
        Запуск TaskManager
        :param websocket: объект - соединение с пользователем
        """

        # print("TaskManager запущен")
        await asyncio.gather(self.process_task(),
                             self.get_response(websocket))

    async def process_task(self) -> None:
        """
        Запускает задачи по мере поступления
        """
        while self.running:
            print(1)
            # print("1")
            # print(self.queue_tasks)
            task_info = await self.queue_tasks.get()
            print("2")
            function = task_info["function"]
            id_task = task_info["id_task"]
            websocket = task_info["websocket"]

            params = task_info["params"]
            #print(params)
            timeout = task_info.get("timeout")
            if timeout:
                print("timeout")
                task = asyncio.create_task(
                    self.run_with_timeout(function(id_task, websocket, *params), id_task, timeout)
                )
            else:
                print("timeout -")
                task = asyncio.create_task(function(id_task, websocket, *params))
            print("3")
            self.tasks_in_progress.add(task)
            task.add_done_callback(lambda x: self.remove_task(x))
            print("Здача запущена")
    async def run_with_timeout(self, function, id_task: str, timeout: int):
        """
        Ожидает выполнения функции по заданному времени

        :param function: функция
        :param id_task: id задачи
        :param timeout: время, после которого задача завершиться

        :return: возвращает awaitable по истечении времени(для запуска внутри другой функции)
        """
        try:
            return await asyncio.wait_for(function, timeout=timeout)
        except Exception as e:
            print(f"Задача{id_task} завершилась с ошибкой{e}")

    async def get_response(self, websocket):
        """
        Получает все ответы на задачи от сервера, заменяет future на реальное значение ->
        -> показывает, что ответ на задачу получен

        :param websocket: объект - соединение с пользователем
        """
        async for response in websocket:
            t_response = json.loads(response)
            print("1", t_response)

            if t_response["id_task"] in self.id_response:

                future = self.id_response[t_response["id_task"]]
                #print(self.id_response[t_response["id_task"]])
                #print(future.done())

                if not future.done():
                    future.set_result(t_response["response"])
                    print("1", self.id_response[t_response["id_task"]])

                del self.id_response[t_response["id_task"]]
          #self.id_response[t_response["id_task"]] = t_response["response"]

    async def stop(self):
        """
        Завершает все задачи принудительно
        """
        self.running = False

        for task in self.tasks_in_progress:
            task.cancel()

    def remove_task(self, task):
        """
        Callback-функция, удаляет завершившуюся задачу из списка запущенных задач

        :param task: задача
        Вызывается автоматически при завершении функции
        """
        if task in self.tasks_in_progress:
            self.tasks_in_progress.remove(task)


# Создание задачи:
# await self.task_manager.add_task(self.methodename, str(uuid.uuid4()), websocket, *input_data)
class Client:
    def __init__(self):
        """
        temp_id - временное id пользователя
        user_id - постоянное
        task_manager - TaskManager()
        """
        self.temp_id = str(uuid.uuid4())  # временный id
        self.user_id = ""  # @user_id
        self.task_manager = TaskManager()
        self.notifications = set()

    async def connect(self):
        """
        Создает соединение с сервером, основное тело клиента
        """
        async with websockets.connect(url) as websocket:
            print("Подключено")
            try:
                manager_task = asyncio.create_task(self.task_manager.start_tasks(websocket))
                await asyncio.sleep(0.1)
                print("Start")
                reg = await self.task_manager.add_task(self.registration, str(uuid.uuid4()), websocket, name, username, password, "latsnnhfnjf")

                #
                #здесь все запуски задач
                #
                await  manager_task
            except Exception as e:
                print(f"Error: {e}")

    async def get_chats(self, id_task: str, websocket, id_user: str)->None:
        """
        Запрос серверу на получение всех чатов

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param id_user: id пользователя
        """
        await websocket.send(
            json.dumps({"action": "get_chats", "id_task": id_task, "params": [id_user]}))


    async def send_message(self, id_task: str, websocket, message_type: str, text: str, chat_id: str, user_id: str)->None:
        """
        Запрос серверу на отправку сообщения

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param message_type: тип сообщения(text, image и другие)
        :param text: содержимое сообщения(тип - text)
        :param chat_id: id чата, куда отправляется сообщение
        :param user_id: id пользователя, который отправил сообщение
        """
        await websocket.send(
            json.dumps({"action": "create_message", "id_task": id_task, "params": [message_type, text, chat_id, user_id]}))

    async def open_chat(self, id_task: str, websocket, user_id: str)->None:
        """
        Запрос серверу на получение чата(?)

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param user_id: id пользователя
        """
        await websocket.send(
            json.dumps({"action": "open_chat", "id_task": id_task, "params": [user_id]})
        )

    async def registration(self, id_task: str, websocket, name: str, username: str, password: str, lastname: str)->None:
        """
        Запрос серверу на регистрацию

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param name: имя пользователя
        :param username: username пользователя(уникальное имя)
        :param password: пароль
        """
        await websocket.send(
            json.dumps({"action": "registration", "id_task": id_task, "params": [name, username, password]}))

    async def auth(self, id_task: str, websocket, username: str, password: str)->None:
        """
        Запрос серверу на авторизацию

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param username: username пользователя(уникальное имя)
        :param password: пароль
        """
        await websocket.send(
            json.dumps({"action": "auth", "id_task": id_task, "params": [username, password]}))

    async def get_notification(self, id_task: str, websocket, user_id: str)->None:
        """
        Запрос на получение уведомлений пользователю

        :param id_task: id задачи
        :param websocket: объект - соединение с пользователем
        :param user_id: id пользователя
        """
        await websocket.send(
            json.dumps({"action" : "get_notifications", "id_task": id_task, "params": [user_id]}))

    async def clear_note(self)->None:
        """
        Отчищает список уведомлений
        """
        self.notifications.clear()

if __name__ == "__main__":
    client = Client()
    asyncio.run(client.connect())