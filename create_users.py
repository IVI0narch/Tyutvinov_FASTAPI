"""Создаёт 5 начальных пользователей для корректной работы"""

from app.models import User
from app.database import SessionLocal
from app.auth import get_password_hash

def main():
    db = SessionLocal()
    for i in range(1, 6):
        user = User(username=f"user{i}", hashed_password=get_password_hash("password"))
        db.add(user)
    db.commit()
    print("Создано 5 пользователей")
    db.close()

if __name__ == "__main__":
    main()
