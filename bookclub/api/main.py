from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from bookclub.api.schemas import (
    ActivityLogResponse,
    BookCreate,
    BookResponse,
)
from bookclub.database.activity_log_repository import ActivityLogRepository
from bookclub.database.book_repository import BookRepository
from bookclub.domain import (
    Book,
    BookClubError,
    BookNotFoundError,
    BookStatistics,
    DuplicateBookError,
)

app = FastAPI(
    title="BookClub API",
    description="API системы учёта книг в книжном клубе",
    version="1.0.0",
)

repository = BookRepository()
activity_repository = ActivityLogRepository()


@app.exception_handler(BookClubError)
async def book_club_error_handler(request: Request, error: BookClubError):
    """Переводит собственные исключения приложения в HTTP-ответы."""
    if isinstance(error, BookNotFoundError):
        status_code = 404
    elif isinstance(error, DuplicateBookError):
        status_code = 409
    else:
        status_code = 422
    return JSONResponse(status_code=status_code, content={"detail": str(error)})


def to_response(book: Book) -> BookResponse:
    return BookResponse(
        id=book.book_id,
        title=book.title,
        author=book.author,
        genre=book.genre,
        pages=book.pages,
        status=book.status.value,
        suggested_by=book.suggested_by,
        rating=book.rating,
        finished_on=book.finished_on,
    )


def get_book_or_404(book_id: int) -> Book:
    book = repository.get_by_id(book_id)
    if book is None:
        raise BookNotFoundError("Книга не найдена")
    return book


@app.get("/")
def root():
    return {"message": "BookClub API работает"}


@app.get("/books", response_model=list[BookResponse])
def get_books():
    return [to_response(book) for book in repository.get_all()]


@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(data: BookCreate):
    book = Book(**data.model_dump())
    book_id = repository.add(book)
    return to_response(get_book_or_404(book_id))


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    return to_response(get_book_or_404(book_id))


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, data: BookCreate):
    book = Book(**data.model_dump(), book_id=book_id)
    get_book_or_404(book_id)
    if not repository.update(book):
        raise BookNotFoundError("Книга не найдена")
    return to_response(get_book_or_404(book_id))


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if not repository.delete(book_id):
        raise BookNotFoundError("Книга не найдена")


@app.get("/statistics")
def get_statistics():
    stats = BookStatistics(repository.get_all())
    best = stats.best_book
    return {
        "total_count": stats.total_count,
        "by_status": {
            status.value: count
            for status, count in stats.count_by_status().items()
        },
        "average_rating": stats.average_rating,
        "total_pages_read": stats.total_pages_read,
        "best_book": (
            {"title": best.title, "author": best.author, "rating": best.rating}
            if best else None
        ),
        "finished_by_month": [
            {"month": month, "count": count}
            for month, count in stats.finished_by_month().items()
        ],
        "by_genre": [
            {"genre": genre, "count": count}
            for genre, count in stats.count_by_genre().items()
        ],
    }


@app.get("/activity-log", response_model=list[ActivityLogResponse])
def get_activity_log():
    return [
        ActivityLogResponse(
            id=e.log_id, book_id=e.book_id, action=e.action,
            details=e.details, created_at=e.created_at,
        )
        for e in activity_repository.get_all()
    ]


web_directory = Path(__file__).resolve().parents[1] / "web"
app.mount("/web", StaticFiles(directory=web_directory, html=True), name="web")
