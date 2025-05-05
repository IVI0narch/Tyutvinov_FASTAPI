"""
CRUD операции для БД работы с книгами
Включает аутентификацию пользователя, работу с книгами, их авторами, жанрами и рейтингами
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Authentication ---
def get_user_by_username(db: Session, username: str):
    """Получает пользователя по имени"""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Создаёт нового пользователя с хэшированным паролем"""
    hashed_pw = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """Аутентификация по паролю и логину"""
    user = get_user_by_username(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

# --- Genre ---
def create_genre(db: Session, genre: schemas.GenreCreate):
    """Создаёт новый жанр"""
    db_genre = models.Genre(name=genre.name)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

def get_all_genres(db: Session):
    """Все жанры"""
    return db.query(models.Genre).all()

def get_genre(db: Session, genre_id: int):
    """Получает жанр по ID"""
    return db.query(models.Genre).filter(models.Genre.id == genre_id).first()

def update_genre(db: Session, genre_id: int, genre: schemas.GenreCreate):
    """Обновляет название жанра по ID"""
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not db_genre:
        return None
    db_genre.name = genre.name
    db.commit()
    db.refresh(db_genre)
    return db_genre

def delete_genre(db: Session, genre_id: int):
    """Удаляет жанр по ID"""
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not db_genre:
        return None
    db.delete(db_genre)
    db.commit()
    return db_genre

# --- Author ---
def create_author(db: Session, author: schemas.AuthorCreate):
    """Создаёт нового автора"""
    db_author = models.Author(name=author.name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

def get_all_authors(db: Session):
    """Получает весь список авторов"""
    return db.query(models.Author).all()

def get_author(db: Session, author_id: int):
    """Получает автора по ID"""
    return db.query(models.Author).filter(models.Author.id == author_id).first()

def update_author(db: Session, author_id: int, author: schemas.AuthorCreate):
    """Обновляет имя автора по его ID"""
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        return None
    db_author.name = author.name
    db.commit()
    db.refresh(db_author)
    return db_author

def delete_author(db: Session, author_id: int):
    """Удаляет автора по ID"""
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        return None
    db.delete(db_author)
    db.commit()
    return db_author

# --- Book ---
def create_book(db: Session, book: schemas.BookCreate):
    """СОздание новой книги с авторами и жанрами"""
    genres = db.query(models.Genre).filter(models.Genre.id.in_(book.genre_ids)).all()
    authors = db.query(models.Author).filter(models.Author.id.in_(book.author_ids)).all()
    db_book = models.Book(
        title=book.title,
        description=book.description,
        genres=genres,
        authors=authors
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_book(db: Session, book_id: int):
    """Книга по ID"""
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_all_books(db: Session):
    """Получает весь список книг"""
    return db.query(models.Book).all()

def update_book(db: Session, book_id: int, book_data: schemas.BookUpdate):
    """Обновляет информацию по книге, включая жанр и автора"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None
    for attr, value in book_data.dict(exclude_unset=True).items():
        if attr == "genre_ids":
            genres = db.query(models.Genre).filter(models.Genre.id.in_(value)).all()
            book.genres = genres
        elif attr == "author_ids":
            authors = db.query(models.Author).filter(models.Author.id.in_(value)).all()
            book.authors = authors
        elif hasattr(book, attr):
            setattr(book, attr, value)
    db.commit()
    db.refresh(book)
    return book

def delete_book(db: Session, book_id: int):
    """Удаляет книгу по ID"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None
    db.delete(book)
    db.commit()
    return book

# --- Rating ---
def create_rating(db: Session, user_id: int, book_id: int, rating: schemas.RatingCreate):
    """Создаёт рейтинг книги для конкретного пользователя"""
    db_rating = models.Rating(user_id=user_id, book_id=book_id, score=rating.score)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def get_ratings_for_book(db: Session, book_id: int):
    """Получает все оценки книги"""
    return db.query(models.Rating).filter(models.Rating.book_id == book_id).all()

# --- Genre-to-Book ---
def add_genre_to_book(db: Session, book_id: int, genre_id: int):
    """Добавляет жанр к книге"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not book or not genre:
        return None
    if genre not in book.genres:
        book.genres.append(genre)
        db.commit()
    return book

def remove_genre_from_book(db: Session, book_id: int, genre_id: int):
    """Убирает жанр из книги"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not book or not genre:
        return None
    if genre in book.genres:
        book.genres.remove(genre)
        db.commit()
    return book

def get_book_genres(db: Session, book_id: int):
    """Получает все жанры книги"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    return book.genres if book else None
