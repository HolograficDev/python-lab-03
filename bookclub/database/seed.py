"""Заполнение базы демонстрационными данными.

Запуск:
    python -m bookclub.database.seed            # добавить книги
    python -m bookclub.database.seed --clear    # сначала очистить таблицы
"""
import sys
from datetime import date, datetime, timedelta

from bookclub.domain import Book, BookStatus, DuplicateBookError

from .book_repository import BookRepository
from .connection import get_connection


def days_ago(count: int) -> date:
    return date.today() - timedelta(days=count)


# (название, автор, жанр, страниц, кто предложил, оценка, дней назад дочитана)
FINISHED = [
    ("The Master and Margarita", "Mikhail Bulgakov", "Роман", 480, "Анна", 5, 120),
    ("1984", "George Orwell", "Антиутопия", 328, "Максим", 5, 105),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Роман", 672, "Ольга", 4, 92),
    ("The Little Prince", "Antoine de Saint-Exupéry", "Притча", 96, "Анна", 5, 80),
    ("Animal Farm", "George Orwell", "Сатира", 144, "Игорь", 4, 70),
    ("Eugene Onegin", "Alexander Pushkin", "Роман в стихах", 224, "Ольга", 4, 58),
    ("Three Comrades", "Erich Maria Remarque", "Роман", 480, "Максим", 5, 47),
    ("The Catcher in the Rye", "J. D. Salinger", "Роман", 288, "Игорь", 3, 38),
    ("We", "Yevgeny Zamyatin", "Антиутопия", 224, "Анна", 4, 29),
    ("Heart of a Dog", "Mikhail Bulgakov", "Повесть", 160, "Ольга", 5, 18),
]
# Эти две книги сначала добавляются как «Читаем», затем переводятся
# в «Прочитана» — так в журнале появятся записи об изменении.
FINISHED_LATER = [
    ("The Old Man and the Sea", "Ernest Hemingway", "Повесть", 128, "Максим", 4, 9),
    ("Murder on the Orient Express", "Agatha Christie", "Детектив", 288, "Игорь", 4, 4),
]
READING = [
    ("The Idiot", "Fyodor Dostoevsky", "Роман", 640, "Ольга"),
    ("Dune", "Frank Herbert", "Фантастика", 704, "Максим"),
    ("Sapiens", "Yuval Noah Harari", "Научпоп", 512, "Анна"),
]
PLANNED = [
    ("Pride and Prejudice", "Jane Austen", "Роман", 432, "Анна"),
    ("The Three-Body Problem", "Liu Cixin", "Фантастика", 416, "Игорь"),
    ("The Alchemist", "Paulo Coelho", "Притча", 208, "Ольга"),
    ("The Count of Monte Cristo", "Alexandre Dumas", "Приключения", 1312, "Максим"),
    ("Fahrenheit 451", "Ray Bradbury", "Антиутопия", 256, "Анна"),
]


def clear_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            "TRUNCATE TABLE activity_logs, books RESTART IDENTITY;"
        )
    print("Таблицы очищены")


def last_log_id() -> int:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT COALESCE(MAX(id), 0) FROM activity_logs;"
        ).fetchone()
        return row[0]


def spread_log_over_days(first_new_id: int, days: float = 3.5) -> None:
    """Равномерно распределяет новые записи журнала по последним дням."""
    with get_connection() as connection:
        ids = [row[0] for row in connection.execute(
            "SELECT id FROM activity_logs WHERE id > %s ORDER BY id;",
            (first_new_id,),
        ).fetchall()]
        if not ids:
            return
        now = datetime.now().astimezone()
        start = now - timedelta(days=days)
        step = (timedelta(days=days) - timedelta(minutes=30)) / len(ids)
        for index, log_id in enumerate(ids):
            connection.execute(
                "UPDATE activity_logs SET created_at = %s WHERE id = %s;",
                (start + step * index, log_id),
            )


def seed() -> None:
    repository = BookRepository()
    first_new_id = last_log_id()
    added = 0

    def add(book: Book) -> int | None:
        nonlocal added
        try:
            book_id = repository.add(book)
        except DuplicateBookError:
            print(f"Пропущена (уже есть): {book.title}")
            return None
        added += 1
        return book_id

    for title, author, genre, pages, member, rating, ago in FINISHED:
        add(Book(title, author, genre, pages, BookStatus.FINISHED,
                 member, rating, days_ago(ago)))

    for title, author, genre, pages, member in READING:
        add(Book(title, author, genre, pages, BookStatus.READING, member))

    for title, author, genre, pages, member in PLANNED:
        add(Book(title, author, genre, pages, BookStatus.PLANNED, member))

    for title, author, genre, pages, member, rating, ago in FINISHED_LATER:
        book_id = add(Book(title, author, genre, pages,
                           BookStatus.READING, member))
        if book_id:
            repository.update(Book(
                title, author, genre, pages, BookStatus.FINISHED, member,
                rating, days_ago(ago), book_id=book_id))

    # Случайно добавленная и удалённая книга — запись «Удаление» в журнале.
    wrong_id = add(Book("Accidentally Added Book", "Unknown",
                        "Разное", 100, suggested_by="Игорь"))
    if wrong_id:
        repository.delete(wrong_id)
        added -= 1

    spread_log_over_days(first_new_id)
    print(f"Готово: добавлено книг — {added}")


if __name__ == "__main__":
    if "--clear" in sys.argv:
        clear_tables()
    seed()