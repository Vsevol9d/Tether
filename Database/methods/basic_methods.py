"""
Здесь собраны основные методы для всех таблиц
"""

from Database.init import catching_errors

from typing import Generic, TypeVar, Sequence, Any
from sqlalchemy import select, Column, and_
from sqlalchemy.orm import Session

T = TypeVar("T")  # Нужно для правильной аннотации и подсказок


class BasicMethods(Generic[T]):
    def __init__(self, session: Session, model = None):
        self.session = session
        self.model = model

    @staticmethod
    def __get_attributes(obj) -> dict:
        attrs = {}

        # перебор через dir() и getattr, пропуская исключения и приватные, если нужно
        for name in dir(obj):
            if name.startswith('_'):
                continue
            attrs[name] = getattr(obj, name)
        return attrs

    @catching_errors()
    def _get_column(self, attr_name: str) -> Column | None:
        """
        Проверка существования колонки в таблице

        :param attr_name: колонка, существование которой надо проверить
        :return: колонка таблицы
        """

        if not hasattr(self.model, attr_name): return None
            # raise AttributeError(f"Модель {self.model.__name__} не содержит поля '{attr_name}'")
        return getattr(self.model, attr_name)

    @catching_errors()
    def exists(self, **kwargs: Any) -> bool:
        """
        Проверка существования строки по набору колонка=значение,
        например: exists(id=1, name='Nik')
        :return: булевое значение
        """

        conditions = []
        for attr_name, value in kwargs.items():
            column = self._get_column(attr_name)
            if column is None: return False
            conditions.append(column == value)

        stmt = select(self.model).where(and_(*conditions))
        return self.session.execute(stmt).scalar() is not None

    @catching_errors()
    def _get_dict(self, raw_users: Sequence[list]) -> list[dict]:
        structured_users = list()
        for user in raw_users:
            user_dict = self.__get_attributes(user)
            for key, value in user_dict.copy().items():  # Проверка элементов на экземпляр класса
                # Если не объект класса "sqlalchemy" или список, то возращаем
                type_attr = getattr(value, '__module__', '')
                if type_attr.startswith('sqlalchemy.') or type_attr.startswith('Database.'):
                    # Если нужны связанные строки из других таблиц -
                    # and not isinstance(value, InstrumentedList)
                    del user_dict[key]  # Удаление неподходящих атрибутов

            structured_users.append(user_dict)

        return structured_users

    @catching_errors()
    def add(self, **kwargs) -> dict:
        """
        Добавление пользователя в таблицу
        """
        self.session.add(self.model(**kwargs))
        print(f'Запись в таблице {self.model.__name__} добавлена с параметрами {kwargs}')
        return {'isSuccess': True, 'data': kwargs}

    @catching_errors()
    def select_all(self) -> dict:
        """
        Вывод всех значений всех пользователей
        :return: список классов таблицы
        """
        raw_users = self.session.scalars(select(self.model)).all()
        structured_users = self._get_dict(raw_users)
        return {'isSuccess': True, 'data': structured_users}

    @catching_errors()
    def update(self, id: int | list, attr_name: str, value: Any,) -> dict:
        """
        Обновление у пользователя с id = id атрибута attr_name на значение value
        """

        instance = self.session.get(self.model, id)
        setattr(instance, attr_name, value)
        print(f'Запись в таблице {self.model.__name__} '
              f'с id {id} и в колонке {attr_name} обновлена на {value}')
        return {'isSuccess': True}

    @catching_errors()
    def delete(self, *id: list[int | tuple[int, int]]) -> dict:
        """
        Удаление записи с id = id
        """

        ids = id if len(id) > 1 else id[0]
        self.session.delete(self.session.get(self.model, ids))
        print(f'Запись в таблице {self.model.__name__} с id {ids} удалёна')
        return {'isSuccess': True}
