"""Общие фикстуры. Интеграционные тесты работают в отдельной БД bookclub_test."""
import os

import psycopg
import pytest

from bookclub.database.connection import get_connection

TEST_DB_NAME = "bookclub_test"


def _ensure_test_database() -> None:
    """Создаёт тестовую БД и таблицы, если их ещё нет."""
    os.environ.pop("BOOKCLUB_DB_NAME", None)
    with get_connection() as connection:
        connection.autocommit = True
        exists = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;", (TEST_DB_NAME,)
        ).fetchone()
        if not exists:
            connection.execute(f"CREATE DATABASE {TEST_DB_NAME};")

    os.environ["BOOKCLUB_DB_NAME"] = TEST_DB_NAME
    from bookclub.database.schema import create_tables
    create_tables()


@pytest.fixture
def db():
    """Чистая тестовая база для каждого теста."""
    try:
        _ensure_test_database()
    except (psycopg.OperationalError, RuntimeError) as error:
        pytest.skip(f"PostgreSQL недоступен: {error}")

    def truncate():
        with get_connection() as connection:
            connection.execute(
                "TRUNCATE TABLE activity_logs, books RESTART IDENTITY;"
            )

    truncate()
    yield
    truncate()
    os.environ.pop("BOOKCLUB_DB_NAME", None)
