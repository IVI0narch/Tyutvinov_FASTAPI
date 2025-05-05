"""Загружает книги в БД из books.csv"""

import pandas as pd
import random
from sqlalchemy.orm import Session
from app.models import Book, Author, Genre, Rating, User
from app.database import SessionLocal

GENRE_LIST = ["Fantasy", "Science Fiction", "Romance", "Mystery", "Historical", "Thriller", "Non-Fiction"]

def get_or_create_author(db: Session, name: str):
    author = db.query(Author).filter_by(name=name).first()
    if not author:
        author = Author(name=name)
        db.add(author)
    return author

def get_or_create_genre(db: Session, name: str):
    genre = db.query(Genre).filter_by(name=name).first()
    if not genre:
        genre = Genre(name=name)
        db.add(genre)
    return genre

def assign_random_genres(db: Session):
    return [get_or_create_genre(db, genre) for genre in random.sample(GENRE_LIST, k=random.randint(1, 2))]

def assign_fake_ratings(db: Session, book: Book, avg_rating: float):
    users = db.query(User).all()
    if not users:
        print("Нет пользователей в БД — невозможно создать рейтинги.")
        return

    num_ratings = random.randint(3, 10)
    selected_users = random.sample(users, min(num_ratings, len(users)))
    for user in selected_users:
        noise = random.uniform(-0.5, 0.5)
        score = round(min(max(avg_rating + noise, 1), 5), 2)
        rating = Rating(score=score, user_id=user.id, book=book)
        db.add(rating)

def load_books_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path)
    df = df[['bookID', 'title', 'authors', 'average_rating']].dropna()

    # Локальный кэш авторов и жанров по имени
    author_cache = {}
    genre_cache = {}

    for i, row in df.iterrows():
        if db.query(Book).filter_by(id=row['bookID']).first():
            continue

        authors_names = [name.strip() for name in str(row['authors']).split('/')]

        authors = []
        for name in authors_names:
            if name in author_cache:
                authors.append(author_cache[name])
            else:
                existing = db.query(Author).filter_by(name=name).first()
                if existing:
                    author_cache[name] = existing
                else:
                    new_author = Author(name=name)
                    db.add(new_author)
                    db.flush()  # получить ID
                    author_cache[name] = new_author
                authors.append(author_cache[name])

        book = Book(
            id=int(row['bookID']),
            title=str(row['title']),
            description=""
        )

        db.add(book)
        db.flush()  # получить ID книги

        book.authors = authors

        # Случайные жанры — используем кэш
        genres = []
        for genre_name in random.sample(GENRE_LIST, k=random.randint(1, 2)):
            if genre_name in genre_cache:
                genres.append(genre_cache[genre_name])
            else:
                g = db.query(Genre).filter_by(name=genre_name).first()
                if not g:
                    g = Genre(name=genre_name)
                    db.add(g)
                    db.flush()
                genre_cache[genre_name] = g
                genres.append(g)
        book.genres = genres

        assign_fake_ratings(db, book, float(row['average_rating']))
        db.commit()

        if i % 100 == 0:
            print(f"Обработано {i} книг...")

    print(f"Загружено книг: {len(df)}")


def main():
    db = SessionLocal()
    try:
        load_books_from_csv('books.csv', db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
