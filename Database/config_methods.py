"""
Методы для изменения структуры БД
Для работы сервера или UI этот файл не предназначен
"""

from Database.init import Base, engine
from typing import Optional
from pathlib import Path
import subprocess, os
from sqlalchemy import text

def CREATE_ALL_TABLE():
    from Database.models.users import Users
    from Database.models.chats import Chats
    from Database.models.participants import Participants
    from Database.models.messages import Messages
    from Database.models.friends import Friends
    Base.metadata.create_all(engine)  # Создание всех ещё не созданных таблиц

def DROP_ALL():
    # Удаление всех таблиц. :)
    from sqlalchemy import MetaData
    metadata = MetaData()
    metadata.reflect(bind=engine)        # загрузить существующие таблицы
    metadata.drop_all(bind=engine)      # удалить все отражённые таблицы

def ADD_COLUMN(model, column):
    # Добавить колонку в таблицу users
    with engine.connect() as conn:
        conn.execute(text(f"ALTER TABLE {model} ADD COLUMN {column} TEXT"))
        # conn.execute(text("ALTER TABLE chats ADD COLUMN id_last_mes INTEGER DEFAULT 0;"))

        # Присваивание NOT NULL
        # conn.execute(text("ALTER TABLE users ALTER COLUMN password SET NOT NULL;"))
        conn.commit()

def UPDATE_COLUMN(model, column):
    # Добавить колонку в таблицу users
    with engine.connect() as conn:
        conn.execute(text(f"ALTER TABLE {model} ALTER COLUMN {column} TYPE VARCHAR"))
        conn.commit()


class PostgresBackupManager:
    def __init__(self, db_name: str, user: str, password: str, host: str, path_dir_pg: str, port: str = "5432"):
        self.db_name = db_name
        self.user = user
        self.host = host
        self.port = port
        self.env = os.environ.copy()
        self.env["PGPASSWORD"] = password  # Передача пароля без интерактивного ввода
        self.env["PGSSLMODE"] = "require"  # SSL через переменную окружения (работает во всех версиях)

        # 🔧 Формируем полные пути к утилитам
        self.pg_dump = Path(path_dir_pg) / "pg_dump.exe"
        self.pg_restore = Path(path_dir_pg) / "pg_restore.exe"
        self.createdb = Path(path_dir_pg) / "createdb.exe"

    def create_backup(self, backup_path: Path) -> bool:
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(self.pg_dump), "-U", self.user, "-h", self.host, "-p", self.port, "-d", self.db_name,
            "-Fc", "-Z", "3", "-f", str(backup_path)
        ]

        result = subprocess.run(cmd, env=self.env, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Бэкап создан: {backup_path}")
            return True
        print("❌ Ошибка pg_dump:", result.stderr)
        return False

    def restore_backup(self, backup_path: Path, target_db: Optional[str] = None) -> bool:
        target_db = target_db or self.db_name

        # Создание базы (игнорируем ошибку, если уже существует)
        create_cmd = [
            str(self.createdb), "-U", self.user, "-h", self.host, "-p", self.port, target_db
        ]
        subprocess.run(create_cmd, env=self.env, capture_output=True, text=True)

        cmd = [
            str(self.pg_restore), "-U", self.user, "-h", self.host, "-p", self.port, "-d", target_db,
            "-c", "--if-exists", "-j", "4", str(backup_path)
        ]

        result = subprocess.run(cmd, env=self.env, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Восстановление завершено")
            return True
        print("❌ Ошибка pg_restore:", result.stderr)
        return False


# backup = PostgresBackupManager("communicator_kzeo",
#                                "super_admin",
#                                "D6xOVkD3GEk6q7ZIhlPGRspFY40v4mZf",
#                                "dpg-d7r3olnlk1mc73cuqv4g-a.oregon-postgres.render.com",  # текущий хост
#                                r"D:\Programs\PostgreSQL\bin"  # путь к ...\PostgreSQL\bin
#                                )

# Создание
# timestamp = datetime.now().strftime("%Y-%m-%d")
# backup_file = Path(f"backups/db_{timestamp}.dump")
# if backup.create_backup(backup_file):
#     print("Резервная копия создана")

# Восстановление в новую базу (безопасно для тестов)
# backup_file = Path("backups/db_2026-05-19.dump")
# if backup.restore_backup(backup_file):
#     print("Восстановление завершено")


# CREATE_ALL_TABLE()
# ADD_COLUMN('chats', 'last_mes')
# ADD_COLUMN('chats', 'last_sender')
# DROP_ALL()
# CREATE_ALL_TABLE()
UPDATE_COLUMN('users', 'avatar_url')
UPDATE_COLUMN('chats', 'avatar_url')
UPDATE_COLUMN('messages', 'file_id')