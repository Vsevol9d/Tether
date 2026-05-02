from Database.init import Base
from sqlalchemy import Column, String, Integer, Text, text, CheckConstraint
from sqlalchemy.orm import relationship


# Выбор данных для типа сообщения
allowedListMessageTypes = ("private", "group", "channel")

# Таблица chats
class Chats(Base):
    __tablename__ = 'chats'
    __table_args__ = (CheckConstraint(
        f"type IN {allowedListMessageTypes}", name="список разрешенных типов чатов"),)  # Для колонки type

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    avatar_url = Column(Text)
    date_created = Column(String(10), nullable=False, server_default=text("to_char(current_date, 'DD-MM-YYYY')"))
    type = Column(String, nullable=False, default="private")

    participants = relationship("Participants", back_populates="chat", cascade="all, delete-orphan")
    users = relationship("Users", secondary="participants", back_populates="chats", overlaps="participants")
    messages = relationship("Messages", back_populates="chat", cascade="all, delete-orphan")