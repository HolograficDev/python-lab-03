from datetime import date

from bookclub.domain import Book, BookStatistics, BookStatus


def finished(title, rating, day, pages=300, genre="Роман"):
    return Book(title, "Автор", genre, pages, BookStatus.FINISHED,
                rating=rating, finished_on=day)


def test_empty_statistics():
    stats = BookStatistics([])
    assert stats.total_count == 0
    assert stats.average_rating is None
    assert stats.best_book is None
    assert stats.total_pages_read == 0
    assert stats.finished_by_month() == {}


def test_count_by_status():
    books = [
        Book("A", "x", "g", 10),
        Book("B", "x", "g", 10, BookStatus.READING),
        finished("C", 4, date(2026, 10, 1)),
    ]
    counts = BookStatistics(books).count_by_status()
    assert counts == {
        BookStatus.PLANNED: 1,
        BookStatus.READING: 1,
        BookStatus.FINISHED: 1,
    }


def test_average_rating_and_pages():
    stats = BookStatistics([
        finished("A", 5, date(2026, 10, 1), pages=100),
        finished("B", 3, date(2026, 10, 2), pages=250),
    ])
    assert stats.average_rating == 4.0
    assert stats.total_pages_read == 350


def test_best_book():
    stats = BookStatistics([
        finished("A", 3, date(2026, 10, 1)),
        finished("B", 5, date(2026, 10, 2)),
    ])
    assert stats.best_book.title == "B"


def test_finished_by_month_sorted():
    stats = BookStatistics([
        finished("A", 4, date(2026, 11, 5)),
        finished("B", 4, date(2026, 9, 10)),
        finished("C", 4, date(2026, 9, 20)),
    ])
    assert stats.finished_by_month() == {"2026-09": 2, "2026-11": 1}


def test_count_by_genre():
    stats = BookStatistics([
        finished("A", 4, date(2026, 10, 1), genre="Роман"),
        finished("B", 4, date(2026, 10, 2), genre="Роман"),
        Book("C", "x", "Фантастика", 100),
    ])
    assert stats.count_by_genre() == {"Роман": 2, "Фантастика": 1}
