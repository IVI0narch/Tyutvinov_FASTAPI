# Сброс БД

from app.database import engine
from app import models

def reset_database():
    print("Удаление всех таблиц...")
    models.Base.metadata.drop_all(bind=engine)

    print("Создание всех таблиц...")
    models.Base.metadata.create_all(bind=engine)

    print("База данных успешно сброшена и инициализирована!")

if __name__ == "__main__":
    reset_database()
