from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base

# Таблица связи книга-автор
book_author_table = Table(
    "book_author",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True)
)

# Таблица связи книга-жанр
book_genre_table = Table(
    "book_genre",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True)
)

# Автор
class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", secondary=book_author_table, back_populates="authors")

# Жанр
class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", secondary=book_genre_table, back_populates="genres")

# Книга
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    authors = relationship("Author", secondary=book_author_table, back_populates="books")
    genres = relationship("Genre", secondary=book_genre_table, back_populates="books")
    ratings = relationship("Rating", back_populates="book")

# Пользователь
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    ratings = relationship("Rating", back_populates="user")

# Рейтинг
class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Float, nullable=False)  # от 1 до 5

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    user = relationship("User", back_populates="ratings")
    book = relationship("Book", back_populates="ratings")
