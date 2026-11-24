from datetime import date

import pytest

from bookclub.database.activity_log_repository import ActivityLogRepository
from bookclub.database.book_repository import BookRepository
from bookclub.domain import Book, BookStatus, DuplicateBookError


@pytest.fixture
def repository(db):
    return BookRepository()


def new_book(**overrides):
    data = dict(title="1984", author="Джордж Оруэлл",
                genre="Антиутопия", pages=328)
    data.update(overrides)
    return Book(**data)


def test_crud_and_activity_log(repository):
    book_id = repository.add(new_book())
    assert isinstance(book_id, int)

    saved = repository.get_by_id(book_id)
    assert saved.title == "1984"
    assert saved.status is BookStatus.PLANNED
    assert len(repository.get_all()) == 1

    updated = new_book(status="finished", rating=5,
                       finished_on=date(2026, 10, 15), book_id=book_id)
    assert repository.update(updated) is True
    assert repository.get_by_id(book_id).rating == 5

    assert repository.delete(book_id) is True
    assert repository.get_by_id(book_id) is None

    actions = [e.action for e in reversed(ActivityLogRepository().get_all())]
    assert actions == ["created", "updated", "deleted"]


def test_duplicate_book_rejected(repository):
    repository.add(new_book())
    with pytest.raises(DuplicateBookError):
        repository.add(new_book())


def test_update_and_delete_missing_book(repository):
    assert repository.update(new_book(book_id=999)) is False
    assert repository.delete(999) is False
