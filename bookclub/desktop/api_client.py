import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

logger = logging.getLogger(__name__)

DEFAULT_API_URL = os.getenv("BOOKCLUB_API_URL", "http://127.0.0.1:8000")


class ApiError(Exception):
    """Сервер вернул ошибку (некорректные данные, не найдено, дубликат)."""


class ApiConnectionError(ApiError):
    """Не удалось связаться с сервером API."""


class BookClubAPI:
    """Клиент REST API: единственная точка общения GUI с сервером."""

    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, data: dict | None = None):
        url = f"{self.base_url}{path}"
        try:
            response = httpx.request(method, url, json=data, timeout=5.0)
        except httpx.HTTPError as error:
            logger.error("Нет связи с API: %s %s", method, url)
            raise ApiConnectionError(
                "Не удалось подключиться к серверу. "
                "Убедитесь, что FastAPI запущен."
            ) from error

        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            logger.warning("%s %s -> %s: %s",
                           method, path, response.status_code, detail)
            raise ApiError(str(detail))

        logger.info("%s %s -> %s", method, path, response.status_code)
        return None if response.status_code == 204 else response.json()

    def get_books(self) -> list[dict]:
        return self._request("GET", "/books")

    def create_book(self, data: dict) -> dict:
        return self._request("POST", "/books", data)

    def update_book(self, book_id: int, data: dict) -> dict:
        return self._request("PUT", f"/books/{book_id}", data)

    def delete_book(self, book_id: int) -> None:
        self._request("DELETE", f"/books/{book_id}")

    def get_statistics(self) -> dict:
        return self._request("GET", "/statistics")

    def get_activity_log(self) -> list[dict]:
        return self._request("GET", "/activity-log")
