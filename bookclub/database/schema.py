from .connection import get_connection


def create_tables() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    pages INTEGER NOT NULL CHECK (pages > 0),
                    status VARCHAR(10) NOT NULL
                        CHECK (status IN ('planned', 'reading', 'finished')),
                    suggested_by TEXT NOT NULL DEFAULT '',
                    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                    finished_on DATE,
                    UNIQUE (title, author)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    book_id BIGINT NOT NULL,
                    action VARCHAR(10) NOT NULL
                        CHECK (action IN ('created', 'updated', 'deleted')),
                    details TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
    print("Таблицы базы данных созданы")


if __name__ == "__main__":
    create_tables()
