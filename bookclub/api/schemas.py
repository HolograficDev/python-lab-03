from datetime import date, datetime

from pydantic import BaseModel


class BookCreate(BaseModel):
    """Тело запроса на создание/изменение книги.

    Бизнес-проверки намеренно выполняет доменный класс Book, чтобы
    ошибки возвращались собственными исключениями приложения.
    """

    title: str
    author: str
    genre: str
    pages: int
    status: str = "planned"
    suggested_by: str = ""
    rating: int | None = None
    finished_on: date | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    pages: int
    status: str
    suggested_by: str
    rating: int | None
    finished_on: date | None


class ActivityLogResponse(BaseModel):
    id: int
    book_id: int
    action: str
    details: str
    created_at: datetime
