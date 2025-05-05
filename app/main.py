"""Основной модуль приложения FastAPI для управления книгами, жанрами, рейтингами и пользователями."""

from typing import List, Optional, Dict

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasic
from sqlalchemy.orm import Session

from app import auth, models, schemas, crud, stats
from app.auth import get_current_user
from app.database import engine, SessionLocal

# Создание экземпляра приложения FastAPI
app = FastAPI()

# Создание таблиц при запуске
models.Base.metadata.create_all(bind=engine)

# Для Basic Auth (логин/пароль)
security = HTTPBasic()


def get_db():
    """Получение сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    """Корневой эндпоинт, проверка готовности приложения."""
    return {"message": "Схема БД и связи готовы!"}


# --- Books ---
@app.post("/books/", response_model=schemas.BookRead)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """Создать книгу."""
    return crud.create_book(db, book)


@app.get("/books/", response_model=List[schemas.BookRead])
def read_books(db: Session = Depends(get_db)):
    """Получить список всех книг."""
    return crud.get_all_books(db)


@app.get("/books/{book_id}", response_model=schemas.BookRead)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """Получить книгу по ID."""
    db_book = crud.get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return db_book


@app.put("/books/{book_id}", response_model=schemas.BookRead)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    """Обновить книгу по ID."""
    db_book = crud.update_book(db, book_id, book)
    if not db_book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return db_book


@app.delete("/books/{book_id}", response_model=schemas.BookRead)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Удалить книгу по ID."""
    db_book = crud.delete_book(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return db_book


@app.get("/books/{book_id}/ratings", response_model=List[schemas.RatingRead])
def get_ratings(book_id: int, db: Session = Depends(get_db)):
    """Получить все рейтинги книги."""
    return crud.get_ratings_for_book(db, book_id)


# --- Genres ---
@app.post("/genres/", response_model=schemas.GenreRead)
def create_genre(genre: schemas.GenreCreate, db: Session = Depends(get_db)):
    """Создать жанр."""
    return crud.create_genre(db, genre)


@app.get("/genres/", response_model=List[schemas.GenreRead])
def read_genres(db: Session = Depends(get_db)):
    """Получить все жанры."""
    return crud.get_all_genres(db)


@app.get("/genres/{genre_id}", response_model=schemas.GenreRead)
def read_genre(genre_id: int, db: Session = Depends(get_db)):
    """Получить жанр по ID."""
    genre = crud.get_genre(db, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    return genre


@app.put("/genres/{genre_id}", response_model=schemas.GenreRead)
def update_genre(genre_id: int, genre: schemas.GenreCreate, db: Session = Depends(get_db)):
    """Обновить жанр по ID."""
    db_genre = crud.update_genre(db, genre_id, genre)
    if not db_genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    return db_genre


@app.delete("/genres/{genre_id}", response_model=schemas.GenreRead)
def delete_genre(genre_id: int, db: Session = Depends(get_db)):
    """Удалить жанр по ID."""
    db_genre = crud.delete_genre(db, genre_id)
    if not db_genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    return db_genre


# --- Genre-to-book ---
@app.post("/books/{book_id}/genres/{genre_id}", response_model=schemas.BookRead)
def link_genre(book_id: int, genre_id: int, db: Session = Depends(get_db)):
    """Привязать жанр к книге."""
    result = crud.add_genre_to_book(db, book_id, genre_id)
    if not result:
        raise HTTPException(status_code=404, detail="Книга или жанр не найдены")
    return result


@app.delete("/books/{book_id}/genres/{genre_id}", response_model=schemas.BookRead)
def unlink_genre(book_id: int, genre_id: int, db: Session = Depends(get_db)):
    """Отвязать жанр от книги."""
    result = crud.remove_genre_from_book(db, book_id, genre_id)
    if not result:
        raise HTTPException(status_code=404, detail="Книга или жанр не найдены")
    return result


@app.get("/books/{book_id}/genres", response_model=List[schemas.GenreRead])
def get_book_genres(book_id: int, db: Session = Depends(get_db)):
    """Получить жанры книги."""
    genres = crud.get_book_genres(db, book_id)
    if genres is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return genres


# --- Ratings ---
@app.post("/books/{book_id}/rate", response_model=schemas.RatingRead)
def rate_book(
    book_id: int,
    rating: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Оценить книгу от имени текущего пользователя."""
    return crud.create_rating(db, user_id=current_user.id, book_id=book_id, rating=rating)


# --- Users ---
@app.post("/register", response_model=schemas.UserRead)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Зарегистрировать нового пользователя."""
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Получить токен по логину и паролю."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserRead)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """Получить информацию о текущем пользователе."""
    return current_user


@app.get("/stats/top-books")
def stats_top_books(db: Session = Depends(get_db)):
    return {
        "top_books": stats.get_top_books(db),
        "top_authors": stats.get_top_authors(db)
    }

@app.get("/stats/top-authors")
def stats_top_authors(db: Session = Depends(get_db)):
    return {
        "top_books": stats.get_top_books(db),
        "top_authors": stats.get_top_authors(db)
    }

# --- Authors ---
@app.post("/authors/", response_model=schemas.AuthorRead)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    """Создать автора"""
    return crud.create_author(db, author)

@app.get("/authors/", response_model=List[schemas.AuthorRead])
def read_authors(db: Session = Depends(get_db)):
    """Считать всех авторов"""
    return crud.get_all_authors(db)

@app.get("/authors/{author_id}", response_model=schemas.AuthorRead)
def read_author(author_id: int, db: Session = Depends(get_db)):
    """Получить автора по id"""
    author = crud.get_author(db, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return author

@app.put("/authors/{author_id}", response_model=schemas.AuthorRead)
def update_author(author_id: int, author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    """Обновить автора"""
    db_author = crud.update_author(db, author_id, author)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author

@app.delete("/authors/{author_id}", response_model=schemas.AuthorRead)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    """Удалить автора"""
    db_author = crud.delete_author(db, author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author
