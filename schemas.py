"""Схемы сущностей БД"""

from typing import List, Optional
from pydantic import BaseModel
from pydantic.config import ConfigDict

# --- Author ---
class AuthorBase(BaseModel):
    name: str

class AuthorCreate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Genre ---
class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class GenreRead(GenreBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Book ---
class BookBase(BaseModel):
    title: str
    description: Optional[str] = None

class BookCreate(BookBase):
    genre_ids: List[int]
    author_ids: List[int]

class BookUpdate(BookBase):
    genre_ids: Optional[List[int]] = None
    author_ids: Optional[List[int]] = None

class BookRead(BookBase):
    id: int
    authors: List[AuthorRead] = []
    genres: List[GenreRead] = []

    model_config = ConfigDict(from_attributes=True)

# --- User ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

# --- Rating ---
class RatingBase(BaseModel):
    score: float

class RatingCreate(RatingBase):
    pass

class RatingRead(RatingBase):
    id: int
    book_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Stats ---
class StatsRead(BaseModel):
    top_books: List[BookRead]
    top_authors: List[AuthorRead]

    model_config = ConfigDict(from_attributes=True)
