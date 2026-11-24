import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[2]


def get_connection() -> psycopg.Connection:
    """Открывает соединение с PostgreSQL по настройкам из .env."""
    load_dotenv(PROJECT_DIR / ".env")

    password = os.getenv("BOOKCLUB_DB_PASSWORD")
    if not password:
        raise RuntimeError("Не задан пароль BOOKCLUB_DB_PASSWORD (см. .env)")

    return psycopg.connect(
        host=os.getenv("BOOKCLUB_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("BOOKCLUB_DB_PORT", "5433")),
        dbname=os.getenv("BOOKCLUB_DB_NAME", "bookclub"),
        user=os.getenv("BOOKCLUB_DB_USER", "bookclub"),
        password=password,
    )
