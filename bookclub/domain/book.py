from dataclasses import dataclass
from datetime import date
from enum import Enum

from .exceptions import (
    InvalidBookDataError,
    InvalidRatingError,
    InvalidStatusError,
)


class BookStatus(str, Enum):
    PLANNED = "planned"
    READING = "reading"
    FINISHED = "finished"

    @property
    def title(self) -> str:
        return {
            BookStatus.PLANNED: "В планах",
            BookStatus.READING: "Читаем",
            BookStatus.FINISHED: "Прочитана",
        }[self]

    @classmethod
    def parse(cls, value: "str | BookStatus") -> "BookStatus":
        try:
            return cls(value)
        except ValueError:
            raise InvalidStatusError(
                f"Недопустимый статус книги: {value!r}"
            ) from None


@dataclass
class Book:
    title: str
    author: str
    genre: str
    pages: int
    status: BookStatus = BookStatus.PLANNED
    suggested_by: str = ""
    rating: int | None = None
    finished_on: date | None = None
    book_id: int | None = None

    def __post_init__(self):
        self.title = self.title.strip()
        self.author = self.author.strip()
        self.genre = self.genre.strip()
        self.suggested_by = self.suggested_by.strip()
        self.status = BookStatus.parse(self.status)

        if not self.title:
            raise InvalidBookDataError("Название книги не может быть пустым")
        if not self.author:
            raise InvalidBookDataError("Автор не может быть пустым")
        if not self.genre:
            raise InvalidBookDataError("Жанр не может быть пустым")
        if self.pages <= 0:
            raise InvalidBookDataError(
                "Количество страниц должно быть больше нуля"
            )

        if self.status is BookStatus.FINISHED:
            if self.finished_on is None:
                raise InvalidBookDataError(
                    "Для прочитанной книги укажите дату окончания чтения"
                )
            if self.rating is not None and not 1 <= self.rating <= 5:
                raise InvalidRatingError("Оценка должна быть от 1 до 5")
        else:
            if self.rating is not None:
                raise InvalidRatingError(
                    "Оценку можно поставить только прочитанной книге"
                )
            if self.finished_on is not None:
                raise InvalidBookDataError(
                    "Дата окончания чтения указывается только "
                    "для прочитанных книг"
                )

    @property
    def is_finished(self) -> bool:
        return self.status is BookStatus.FINISHED
