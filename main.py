# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from Database.api import Session, DataBase
from typing import Dict
import json

app = FastAPI()


# 🔹 Хранилище активных подключений: user_id → WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ Пользователь {user_id} подключился")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"❌ Пользователь {user_id} отключился")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast(self, message: dict):
        for conn in self.active_connections.values():
            await conn.send_json(message)


manager = ConnectionManager()


# 🔹 HTTP-эндпоинты (для простых запросов)
class CommandRequest(BaseModel):
    command: str
    username: str


@app.get("/")
def read_root():
    return {"status": "Tether API is running 🚀"}


@app.post("/api/check-user")
def check_user(request: CommandRequest):
    try:
        with Session() as session:
            db = DataBase(session)
            if request.command == "exists":
                result = db.users.exists(username=request.username)
                return result
            else:
                raise ValueError(f"Неизвестная команда: {request.command}")
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


# 🔹 WebSocket-эндпоинт для чата
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Ждём сообщение от клиента
            data = await websocket.receive_text()
            message = json.loads(data)

            # Обработка команд
            if message.get("type") == "chat_message":
                # Сохраняем в БД
                with Session() as session:
                    db = DataBase(session)
                    # ... логика сохранения сообщения ...

                # Отправляем получателю (если он онлайн)
                recipient = message.get("to")
                if recipient:
                    await manager.send_personal_message({
                        "type": "new_message",
                        "from": user_id,
                        "text": message.get("text"),
                        "timestamp": message.get("timestamp")
                    }, recipient)

                # Подтверждение отправителю
                await websocket.send_json({
                    "type": "message_sent",
                    "status": "delivered"
                })

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"❌ Ошибка в WebSocket: {e}")
        manager.disconnect(user_id)