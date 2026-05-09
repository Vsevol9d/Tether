import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI()

# Берем URL из Render (внутри Render он будет внутренним, снаружи - внешним)
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Переменная DATABASE_URL не найдена!")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@app.get("/")
def read_root():
    return {"message": "Server is running!"}

@app.get("/test-db")
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            return {"db_status": "OK", "version": result.scalar()}
    except Exception as e:
        return {"db_status": "ERROR", "error": str(e)}