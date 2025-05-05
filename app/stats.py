"""Решение бизнес задачи --- топ книг"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas


def get_top_books(db: Session, limit: int = 3, genre: Optional[str] = None) -> list[schemas.BookRead]:
    """Выдаёт топ 3 книги по рейтингу"""
    query = db.query(
        models.Book,
        func.avg(models.Rating.score).label("average_rating")
    ).join(models.Rating).group_by(models.Book.id).order_by(func.avg(models.Rating.score).desc())

    books = [book for book, _ in query.limit(limit).all()]
    return [schemas.BookRead.from_orm(book) for book in books]


def get_top_authors(db: Session, limit: int = 3) -> list[schemas.AuthorRead]:
    """Выдаёт топ 3 автора по рейтингу их книг"""
    top_authors = db.query(
        models.Author,
        func.avg(models.Rating.score).label("average_rating")
    ).join(models.book_author_table, models.book_author_table.c.author_id == models.Author.id) \
     .join(models.Book, models.Book.id == models.book_author_table.c.book_id) \
     .join(models.Rating, models.Rating.book_id == models.Book.id) \
     .group_by(models.Author.id) \
     .order_by(func.avg(models.Rating.score).desc()) \
     .limit(limit) \
     .all()

    return [schemas.AuthorRead.from_orm(author) for author, _ in top_authors]
