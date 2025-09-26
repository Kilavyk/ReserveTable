# python create_db.py
import os
import sys
from contextlib import contextmanager
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Загружаем переменные окружения
load_dotenv()

DB_CONFIG = {
    "dbname": "postgres",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

DB_NAME = os.getenv("DB_NAME")


@contextmanager
def postgres_connection(**kwargs):
    """Контекстный менеджер для подключения к PostgreSQL"""
    conn = None
    try:
        conn = psycopg2.connect(**kwargs)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        yield conn
    finally:
        if conn:
            conn.close()


def check_env_vars():
    """Проверка обязательных переменных окружения"""
    required_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Ошибка: отсутствуют переменные окружения: {', '.join(missing_vars)}")
        sys.exit(1)


def database_exists(cursor, db_name):
    """Проверяет существование базы данных"""
    cursor.execute(
        "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
        (db_name,)
    )
    return cursor.fetchone() is not None


def main():
    check_env_vars()

    try:
        with postgres_connection(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                if database_exists(cursor, DB_NAME):
                    print(f"База данных '{DB_NAME}' уже существует.")
                    return

                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
                )
                print(f"База данных '{DB_NAME}' успешно создана!")

    except psycopg2.OperationalError as e:
        print(f"""Ошибка подключения к PostgreSQL: {e}
    Убедитесь, что:
    - PostgreSQL запущен
    - Пользователь и пароль верные""")
        sys.exit(1)

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
