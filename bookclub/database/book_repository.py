from psycopg import errors

from bookclub.domain import Book, BookStatus, DuplicateBookError

from .connection import get_connection

_COLUMNS = (
    "id, title, author, genre, pages, status, "
    "suggested_by, rating, finished_on"
)


def _row_to_book(row) -> Book:
    return Book(
        book_id=row[0],
        title=row[1],
        author=row[2],
        genre=row[3],
        pages=row[4],
        status=BookStatus(row[5]),
        suggested_by=row[6],
        rating=row[7],
        finished_on=row[8],
    )


def _write_log(cursor, book_id: int, action: str, details: str) -> None:
    cursor.execute(
        "INSERT INTO activity_logs (book_id, action, details) "
        "VALUES (%s, %s, %s);",
        (book_id, action, details),
    )


class BookRepository:
    """CRUD-операции над таблицей books с записью в журнал действий."""

    def add(self, book: Book) -> int:
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO books (title, author, genre, pages,
                            status, suggested_by, rating, finished_on)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """,
                        (book.title, book.author, book.genre, book.pages,
                         book.status.value, book.suggested_by,
                         book.rating, book.finished_on),
                    )
                    book_id = cursor.fetchone()[0]
                    _write_log(cursor, book_id, "created",
                               f"Добавлена книга «{book.title}»")
                    return book_id
        except errors.UniqueViolation:
            raise DuplicateBookError(
                f"Книга «{book.title}» ({book.author}) уже есть в клубе"
            ) from None

    def get_all(self) -> list[Book]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT {_COLUMNS} FROM books ORDER BY id;")
                return [_row_to_book(row) for row in cursor.fetchall()]

    def get_by_id(self, book_id: int) -> Book | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT {_COLUMNS} FROM books WHERE id = %s;",
                    (book_id,),
                )
                row = cursor.fetchone()
                return _row_to_book(row) if row else None

    def update(self, book: Book) -> bool:
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE books
                        SET title = %s, author = %s, genre = %s, pages = %s,
                            status = %s, suggested_by = %s, rating = %s,
                            finished_on = %s
                        WHERE id = %s;
                        """,
                        (book.title, book.author, book.genre, book.pages,
                         book.status.value, book.suggested_by, book.rating,
                         book.finished_on, book.book_id),
                    )
                    if cursor.rowcount == 0:
                        return False
                    _write_log(cursor, book.book_id, "updated",
                               f"Изменена книга «{book.title}»")
                    return True
        except errors.UniqueViolation:
            raise DuplicateBookError(
                f"Книга «{book.title}» ({book.author}) уже есть в клубе"
            ) from None

    def delete(self, book_id: int) -> bool:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM books WHERE id = %s RETURNING title;",
                    (book_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    return False
                _write_log(cursor, book_id, "deleted",
                           f"Удалена книга «{row[0]}»")
                return True
