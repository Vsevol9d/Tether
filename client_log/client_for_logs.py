import asyncio

import websockets
import json

import ssl

url = "wss://tether-jj4v.onrender.com/ws"
file_for_logs = 'logs.txt'
class ClientForLogs():
    def __init__(self):
        self.PASSWORD = "SuperSlognyiParol"

    async def connect(self):
        """
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        , ssl=ssl_context"""
        print("Подключаемся")
        for i in range(10):
            try:
                async with websockets.connect(url) as websocket:
                    print("Подключился")
                    await websocket.send(json.dumps({"action": "auth_for_log", "id_task": "1", "params": [self.PASSWORD]}))
                    await asyncio.sleep(1)
                    async for message in websocket:

                        message = json.loads(message)
                        print(message)
                        if "[LOG]" in message:
                            print(message)

                break
            except Exception as e:
                print(f"Error: {e}, пробуем еще раз")

if __name__ == "__main__":
    client = ClientForLogs()
    asyncio.run(client.connect())