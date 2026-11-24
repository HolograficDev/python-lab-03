from datetime import date

import pytest

from bookclub.domain import (
    Book, BookStatus, InvalidBookDataError,
    InvalidRatingError, InvalidStatusError,
)


def make_book(**overrides) -> Book:
    data = dict(title="Дюна", author="Фрэнк Герберт",
                genre="Фантастика", pages=700)
    data.update(overrides)
    return Book(**data)


def test_default_values():
    book = make_book()
    assert book.status is BookStatus.PLANNED
    assert book.rating is None
    assert book.finished_on is None
    assert book.book_id is None


def test_text_fields_are_stripped():
    book = make_book(title="  Дюна  ", author=" Герберт ")
    assert book.title == "Дюна"
    assert book.author == "Герберт"


def test_finished_book_with_rating():
    book = make_book(status="finished", rating=5,
                     finished_on=date(2026, 10, 1))
    assert book.is_finished
    assert book.rating == 5


@pytest.mark.parametrize("field", ["title", "author", "genre"])
def test_empty_text_fields_rejected(field):
    with pytest.raises(InvalidBookDataError):
        make_book(**{field: "   "})


@pytest.mark.parametrize("pages", [0, -5])
def test_invalid_pages(pages):
    with pytest.raises(InvalidBookDataError):
        make_book(pages=pages)


def test_invalid_status():
    with pytest.raises(InvalidStatusError):
        make_book(status="burned")


@pytest.mark.parametrize("rating", [0, 6, -1])
def test_rating_out_of_range(rating):
    with pytest.raises(InvalidRatingError):
        make_book(status="finished", rating=rating,
                  finished_on=date(2026, 10, 1))


def test_rating_for_unfinished_book_rejected():
    with pytest.raises(InvalidRatingError):
        make_book(status="reading", rating=4)


def test_finished_book_requires_date():
    with pytest.raises(InvalidBookDataError):
        make_book(status="finished", rating=4)


def test_date_for_unfinished_book_rejected():
    with pytest.raises(InvalidBookDataError):
        make_book(status="planned", finished_on=date(2026, 10, 1))
