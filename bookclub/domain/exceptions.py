"""Собственные исключения приложения «Книжный клуб»."""


class BookClubError(Exception):
    """Базовое исключение приложения."""


class InvalidBookDataError(BookClubError):
    """Некорректные данные книги (пустое название, число страниц и т.д.)."""


class InvalidStatusError(BookClubError):
    """Недопустимый статус книги."""


class InvalidRatingError(BookClubError):
    """Оценка вне диапазона 1–5 или указана для непрочитанной книги."""


class BookNotFoundError(BookClubError):
    """Книга с указанным идентификатором не найдена."""


class DuplicateBookError(BookClubError):
    """Книга с таким названием и автором уже есть в клубе."""
