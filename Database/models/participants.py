from Database.init import Base
from sqlalchemy import Column, Integer, ForeignKey, text, String, CheckConstraint
from sqlalchemy.orm import relationship


# Выбор данных для роли участника чата
allowedListUserRoles = ("Участник", "Пре-админ", "Админ")

class Participants(Base):
    __tablename__ = 'participants'
    __table_args__ = (CheckConstraint(
        f"role IN {allowedListUserRoles}", name="allowed list of user roles"),)  # Для колонки type


    # composite PK ensures uniqueness: a user can be in a chat only once
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    joined_at = Column(String(19), nullable=False, server_default=text("to_char(current_timestamp, 'DD-MM-YYYY HH24:MI:SS')"))
    role = Column(String, nullable=False, default="Участник")

    chat = relationship("Chats", back_populates="participants", overlaps="users,chats")
    user = relationship("Users", back_populates="participants", overlaps="users,chats")
