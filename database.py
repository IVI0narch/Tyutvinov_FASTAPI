import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Путь к БД-файлу
DB_FOLDER = "data"
DB_FILENAME = "catalog.db"
DB_PATH = os.path.join(DB_FOLDER, DB_FILENAME)

# Создаём папку data, если нет
os.makedirs(DB_FOLDER, exist_ok=True)

# Подключение к SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
