from Database.init import Base
from sqlalchemy import Column, Integer, ForeignKey, String, CheckConstraint, BigInteger
from sqlalchemy.orm import relationship
import sqlalchemy as sql


# Ключ - допустимый тип данных для сообщения
# Значение - то, что будет отображаться в окне чатов, если сообщение с этим типом будет последним в чате
allowed_types = {
    "text": "Текстовая информация", # Затем измениться на текст сообщения (отображаться не должно)
    "file": "Файл",
    "image": "Изображение",
    "video": "Видео"
}


# Таблица messages
class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = (CheckConstraint(
        f"type IN {tuple(allowed_types.keys())}", name="список разрешенных типов сообщений"),)  # Для колонки type

    id = Column(BigInteger, primary_key=True)
    type = Column(String, nullable=False, default="text")
    text = Column(String(4096))
    file_id = Column(Integer)
    creation_date_time = Column(String(19), nullable=False, server_default=sql.text("to_char(current_timestamp, 'DD-MM-YYYY HH24:MI:SS')"))
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    sender_name = Column(String, nullable=True)

    chat = relationship("Chats", back_populates="messages")
    sender = relationship("Users", back_populates="messages")
