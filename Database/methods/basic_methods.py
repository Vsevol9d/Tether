"""
Здесь собраны основные методы для всех таблиц
"""

from Database.init import catching_errors

from typing import Generic, TypeVar, Any
from sqlalchemy import select, inspect, and_
from sqlalchemy.orm import Session

T = TypeVar("T")  # Нужно для правильной аннотации и подсказок


def get_dict(obj: Any):
    """
    Принимает на входе модель таблицы
    Возращает словарь колонок и их значений
    """
    # inspect достаёт только реальные колонки таблицы, игнорируя методы и связи
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


class BasicMethods(Generic[T]):
    def __init__(self, session: Session, model = None):
        self.session = session
        self.model = model

    @catching_errors()
    def exists(self, **kwargs) -> dict:
        """
        Проверка существования значения в определённой строке таблицы

        За параметры функции брать названия колонок в таблице.
        За аргументы - значения, нуждающийся в проверке наличия в данной колонке.
        Например: exists(username='Nikita', name='Nik')

        :return: isSuccess, гда data содержит:
           True, если значение существует.
           False, если значение не существует.
        Например: {'isSuccess': True, 'data': False}
        """

        # Формирование запроса: поиск совпадений по ВСЕМ переданным полям (логика AND)
        # limit(1) останавливает поиск после первой найденной строки (оптимизация)
        stmt = select(self.model).filter_by(**kwargs).limit(1)
        return self.session.execute(stmt).first() is not None

    @catching_errors(commit=True)
    def add(self, **kwargs) -> dict:
        """
        Добавляет новую строку с данными в соответствующую таблицу

        :param kwargs: За параметры функции брать названия колонок в таблице. За аргументы - значения, нуждающийся во вставке в эту колонку. Исключениями (ОНИ ВЕЗДЕ!) являются колонки "id", "date_created", "creation_date_time", "joined_at".
        :return: Словарь isSuccess, где data содержит стандартный словарь, но без колонок-исключений и все значения, указанные как *None* и имеющие значение по умолчанию, вернут *None*
        """

        return self._add(**kwargs)

    @catching_errors(commit=True)
    def add_many(self, *args):
        """
        Добавляет группу строчек с данными в соответствующую таблицу

        Пример: ._add_many({'chat_id': 5, 'user_id': 1}, {'chat_id': 5, 'user_id': 4})
        Пример: ._add_many([{'chat_id': 5, 'user_id': 1}, {'chat_id': 5, 'user_id': 4}])
        :param args: список словарей (можно без "[" и "]"), где один словарь - одна строчка в БД
        :return: Словарь isSuccess, где data содержит стандартный словарь, но без колонок-исключений и все значения, указанные как *None* и имеющие значение по умолчанию, вернут *None*
        """

        return self._add_many(*args)

    @catching_errors()
    def select_all(self) -> list:
        """
        Получает все строки в таблице.

        :return: isSuccess, где data содержит список строк, представленных в виде словарей.
        """

        return self._select_all()

    @catching_errors(commit=True)
    def update(self, pk: int | list, **kwargs) -> dict:
        """
        Обновляет строчку в таблице, через её id.

        :param id: Первичный ключ строки. Если ПК у строки 2 и более, то брать их все через список.
        :param attr_name: Название колонки, значение которой нужно обновить.
        :param value: Значение, на которое нужно обновить поле.
        :return: isSuccess без data ({'isSuccess': True}).
        """
        return self._update(pk, **kwargs)

    @catching_errors(commit=True)
    def delete(self, id: int | tuple[int, int]) -> dict:
        """
        Удаляет строчку в таблице, через её id.

        :param id: Первичный ключ строки. Если ПК у строки 2 и более, то брать их все через список.
        :return: isSuccess без data.
        """

        return self._delete(id)


    def _add(self, **kwargs) -> dict:
        """
        Ядро функции self.add()
        Добавляет новую строку с данными в соответствующую таблицу

        :param kwargs: За параметры функции брать названия колонок в таблице. За аргументы - значения, нуждающийся во вставке в эту колонку. Исключениями (ОНИ ВЕЗДЕ!) являются колонки "id", "date_created", "creation_date_time", "joined_at".
        :return: Словарь isSuccess, где data содержит стандартный словарь, но без колонок-исключений и все значения, указанные как *None* и имеющие значение по умолчанию, вернут *None*
        """

        new_user = self.model(**kwargs)
        self.session.add(new_user)
        self.session.flush()  # коммит, но без закрытия транзакции
        return get_dict(new_user)

    def _add_many(self, *args):
        """
        Ядро функции self.add_many()
        :param args: список словарей (можно без "[" и "]"), где один словарь - одна строчка в БД
        Пример: ._add_many({'chat_id': 5, 'user_id': 1}, {'chat_id': 5, 'user_id': 4})
        Пример: ._add_many([{'chat_id': 5, 'user_id': 1}, {'chat_id': 5, 'user_id': 4}])
        Добавляет группу строчек с данными в соответствующую таблицу
        """
        if type(args[0]) == list: args = args[0]
        # Создание ORM-объектов из всех словарей
        new_objects = [self.model(**user_data) for user_data in args]

        self.session.add_all(new_objects)
        self.session.flush()  # коммит, но без закрытия транзакции

        # Превращение всех объектов в словари (в том числе с id)
        result_list = [get_dict(obj) for obj in new_objects]
        return result_list

    def _select_all(self) -> list[dict]:
        """
        Ядро функции self.select_all()
        Получает все строки в таблице.

        :return: isSuccess, где data содержит список строк, представленных в виде словарей.
        """
        # Получаем ORM-объекты
        raw_users = self.session.scalars(select(self.model)).all()

        # Превращаем каждый объект в словарь
        users_info = []
        for user in raw_users:
            user_dict = get_dict(user)
            users_info.append(user_dict)

        return users_info

    def _update(self, pk: int | list, **kwargs) -> dict:
        """
        Обновляет строчку в таблице, через её id.

        :param pk: Первичный ключ строки. Если ПК у строки 2 и более, то брать их все через список
        :param kwargs: За параметры функции брать названия колонок в таблице
        :param kwargs: За аргументы - значения, нуждающийся в обновлении в данных колонках
        Например: _update(pk=1, username='User2', name='Пользователь2') изменяет username и name там, где id=1
        :return: isSuccess без data ({'isSuccess': True})
        """

        # Получение колонки первичного ключа
        pk_cols = list(self.model.__table__.primary_key.columns)

        # Формирование WHERE (одинарный или составной PK)
        if isinstance(pk, (list, tuple)):
            where_clause = and_(*(col == val for col, val in zip(pk_cols, pk)))
        else:
            where_clause = pk_cols[0] == pk

        # Получение строки
        obj = self.session.execute(select(self.model).where(where_clause)).scalar_one()

        # Обновление всех переданных полей без лишних проверок
        for key, value in kwargs.items():
            setattr(obj, key, value)

        self.session.flush()
        return get_dict(obj)

    def _delete(self, id: int | tuple[int, int]) -> dict:
        """
        Удаляет строчку в таблице, через её id.

        :param id: Первичный ключ строки. Если ПК у строки 2 и более, то брать их все через список.
        :return: isSuccess без data.
        """

        deleted_row = self.session.get(self.model, id)
        row_data = get_dict(deleted_row)
        self.session.delete(deleted_row)
        return row_data
