from collections import Counter
from datetime import date

from .book import Book, BookStatus


class BookStatistics:
    """Расчёт статистики по списку книг клуба."""

    def __init__(self, books: list[Book]):
        self._books = list(books)

    @property
    def total_count(self) -> int:
        return len(self._books)

    def count_by_status(self) -> dict[BookStatus, int]:
        counter = Counter(book.status for book in self._books)
        return {status: counter.get(status, 0) for status in BookStatus}

    @property
    def finished_books(self) -> list[Book]:
        return [book for book in self._books if book.is_finished]

    @property
    def average_rating(self) -> float | None:
        ratings = [b.rating for b in self.finished_books if b.rating]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)

    @property
    def total_pages_read(self) -> int:
        return sum(book.pages for book in self.finished_books)

    @property
    def best_book(self) -> Book | None:
        rated = [b for b in self.finished_books if b.rating]
        return max(rated, key=lambda b: (b.rating, b.pages), default=None)

    def finished_by_month(self) -> dict[str, int]:
        """Количество прочитанных книг по месяцам ('2026-10' -> 3)."""
        result: dict[str, int] = {}
        for book in self.finished_books:
            key = _month_key(book.finished_on)
            result[key] = result.get(key, 0) + 1
        return dict(sorted(result.items()))

    def count_by_genre(self) -> dict[str, int]:
        counter = Counter(book.genre for book in self._books)
        return dict(counter.most_common())


def _month_key(day: date) -> str:
    return f"{day.year}-{day.month:02d}"
