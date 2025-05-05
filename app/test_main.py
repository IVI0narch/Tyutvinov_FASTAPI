"""Тестирование всех функций БД"""

from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def make_unique_name(base: str) -> str:
    return f"{base}_{uuid.uuid4().hex[:8]}"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Схема БД и связи готовы!"}


def test_register_and_login():
    user_data = {
        "username": make_unique_name("testuser"),
        "password": "testpass"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 200

    response = client.post("/token", data=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    return token, user_data["username"]


def test_me():
    token, _ = test_register_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    assert "username" in response.json()


def test_create_and_get_author():
    author_name = make_unique_name("AuthorA")
    author_data = {"name": author_name}
    response = client.post("/authors/", json=author_data)
    assert response.status_code == 200
    author_id = response.json()["id"]

    response = client.get(f"/authors/{author_id}")
    assert response.status_code == 200
    assert response.json()["name"] == author_name

    # Удаление автора
    client.delete(f"/authors/{author_id}")


def test_create_and_get_genre():
    genre_name = make_unique_name("GenreA")
    genre_data = {"name": genre_name}
    response = client.post("/genres/", json=genre_data)
    assert response.status_code == 200
    genre_id = response.json()["id"]

    response = client.get(f"/genres/{genre_id}")
    assert response.status_code == 200
    assert response.json()["name"] == genre_name

    # Удаление жанра
    client.delete(f"/genres/{genre_id}")


def test_create_and_get_book():
    # Уникальные имена
    author_name = make_unique_name("AuthorBook")
    genre_name = make_unique_name("TestGenre")
    book_title = make_unique_name("TestBook")

    # Создание автора
    author_resp = client.post("/authors/", json={"name": author_name})
    assert author_resp.status_code == 200
    author = author_resp.json()

    # Создание жанра
    genre_resp = client.post("/genres/", json={"name": genre_name})
    assert genre_resp.status_code == 200
    genre = genre_resp.json()

    # Создание книги
    book_data = {
        "title": book_title,
        "description": "A book for testing",
        "author_ids": [author["id"]],
        "genre_ids": [genre["id"]],
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200, response.text
    book = response.json()

    # Проверка получения книги
    get_response = client.get(f"/books/{book['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == book_title

    # Удаление книги, автора и жанра
    client.delete(f"/books/{book['id']}")
    client.delete(f"/authors/{author['id']}")
    client.delete(f"/genres/{genre['id']}")


def test_stats_top_books():
    response = client.get("/stats/top-books")
    assert response.status_code == 200
    json_data = response.json()
    assert "top_books" in json_data
    assert "top_authors" in json_data

def test_stats_top_authors():
    response = client.get("/stats/top-authors")
    assert response.status_code == 200
    json_data = response.json()
    assert "top_books" in json_data
    assert "top_authors" in json_data


def test_books_by_author():
    # Уникальные имена
    author_name = make_unique_name("AuthorBook")
    genre_name = make_unique_name("TestGenre")
    book_title = make_unique_name("TestBook")

    # Создание автора
    author_resp = client.post("/authors/", json={"name": author_name})
    assert author_resp.status_code == 200, f"Author creation failed: {author_resp.text}"
    author = author_resp.json()
    print("Created author:", author)  # Логируем ответ для отладки

    # Создание жанра
    genre_resp = client.post("/genres/", json={"name": genre_name})
    assert genre_resp.status_code == 200, f"Genre creation failed: {genre_resp.text}"
    genre = genre_resp.json()
    print("Created genre:", genre)  # Логируем ответ для отладки

    # Создание книги
    book_data = {
        "title": book_title,
        "description": "A book for testing",
        "author_ids": [author["id"]],
        "genre_ids": [genre["id"]],
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200, f"Book creation failed: {response.text}"
    book = response.json()
    print("Created book:", book)  # Логируем ответ для отладки

    # Проверка получения книги
    get_response = client.get(f"/books/{book['id']}")
    assert get_response.status_code == 200, f"Get book failed: {get_response.text}"
    assert get_response.json()["title"] == book_title, f"Book title mismatch: {get_response.json()}"

    # Удаление книги, автора и жанра
    client.delete(f"/books/{book['id']}")
    client.delete(f"/authors/{author['id']}")
    client.delete(f"/genres/{genre['id']}")