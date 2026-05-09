# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse # Для отображения чего-то на сайте (нужно максимум для отладки)
from pydantic import BaseModel
from Database.api import Session, DataBase

app = FastAPI()

# 🔹 Новый эндпоинт для браузера / тестов
@app.get("/")
def read_root():
    # return {
    #     "status": "OK",
    #     "message": "Tether API is running 🚀",
    #     "docs": "Открой /docs для интерактивной документации"
    # }
    html_content = ('<p>"status": "OK"</p>'
                    '<p>"message": "Tether API запускается"</p>'
                    '<p>"docs": "Открой <a href="/docs">/docs</a> для интерактивной документации"</p>')
    return HTMLResponse(content=html_content)

# 🔹 Твой существующий эндпоинт
class CommandRequest(BaseModel):
    command: str
    username: str

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
        raise HTTPException(status_code=500, detail=str(e))