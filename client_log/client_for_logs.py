import asyncio

import websockets
import json

url = "wss://tether-jj4v.onrender.com/ws"
file_for_logs = 'logs.txt'
class ClientForLogs():
    def __init__(self):
        self.PASSWORD = "SuperSlognyiParol"

    async def connect(self):
        async with websockets.connect(url) as websocket:
            print("Подключился")
            await websocket.send(json.dumps({"action": "get_chats", "id_task": "1", "params": [self.PASSWORD]}))
            await asyncio.sleep(1)
            async for message in websocket:
                message = json.loads(message)
                if "[LOG]" in message:
                    print(message)

