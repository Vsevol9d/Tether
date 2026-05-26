from Database.init import Base
from sqlalchemy import Column, Integer, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

# Выбор данных для типа связи
allowedListLevels = (1, 2, 3, 4)
# 1 - знакомые - 2 пользователя состоят в одной группе
# 2 - приятели - имеется личная переписка между двумя пользователями
# 3 - друзья - знают телефон друг друга
# 4 - лучшие друзья - пользователь сам их помечает (на будущие)

# Таблица friends
class Friends(Base):
    __tablename__ = 'friends'
    __table_args__ = (CheckConstraint(                   # Для колонки level_relationships
        f"level_relationships IN {allowedListLevels}", name="список разрешенных связей между пользователями"),)

    user_id_1 = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    user_id_2 = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    level_relationships = Column(Integer, nullable=False, default=1)

    user1 = relationship("Users", back_populates="friend_as_1", foreign_keys=[user_id_1])
    user2 = relationship("Users", back_populates="friend_as_2", foreign_keys=[user_id_2])