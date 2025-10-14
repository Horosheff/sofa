#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

from app.database import engine, Base
from app.models import User, UserSettings

def init_db():
    """Создание всех таблиц в базе данных"""
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()