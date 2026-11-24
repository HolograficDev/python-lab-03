import pytest
from fastapi.testclient import TestClient

from bookclub.api.main import app


@pytest.fixture
def client(db):
    return TestClient(app)


def payload(**overrides):
    data = {"title": "Мастер и Маргарита", "author": "Михаил Булгаков",
            "genre": "Роман", "pages": 480}
    data.update(overrides)
    return data


def test_create_and_get_book(client):
    response = client.post("/books", json=payload())
    assert response.status_code == 201
    book = response.json()
    assert book["status"] == "planned"

    assert client.get(f"/books/{book['id']}").json()["title"] == book["title"]
    assert len(client.get("/books").json()) == 1


def test_update_and_delete(client):
    book_id = client.post("/books", json=payload()).json()["id"]

    changed = payload(status="finished", rating=5, finished_on="2026-10-20")
    response = client.put(f"/books/{book_id}", json=changed)
    assert response.status_code == 200
    assert response.json()["rating"] == 5

    assert client.delete(f"/books/{book_id}").status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404


def test_invalid_data_returns_422(client):
    response = client.post("/books", json=payload(pages=0))
    assert response.status_code == 422
    assert "страниц" in response.json()["detail"]


def test_rating_for_unfinished_book_returns_422(client):
    response = client.post("/books", json=payload(rating=4))
    assert response.status_code == 422


def test_duplicate_returns_409(client):
    client.post("/books", json=payload())
    assert client.post("/books", json=payload()).status_code == 409


def test_missing_book_returns_404(client):
    assert client.get("/books/12345").status_code == 404
    assert client.put("/books/12345", json=payload()).status_code == 404
    assert client.delete("/books/12345").status_code == 404


def test_statistics_and_log(client):
    client.post("/books", json=payload(
        status="finished", rating=4, finished_on="2026-10-20"))
    client.post("/books", json=payload(title="Другая", status="reading"))

    stats = client.get("/statistics").json()
    assert stats["total_count"] == 2
    assert stats["by_status"]["finished"] == 1
    assert stats["average_rating"] == 4.0
    assert stats["finished_by_month"] == [{"month": "2026-10", "count": 1}]

    log = client.get("/activity-log").json()
    assert len(log) == 2
    assert log[0]["action"] == "created"
