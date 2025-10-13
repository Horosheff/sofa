from sqlalchemy import create_engine
from app.models import Base
import os

# URL базы данных
DATABASE_URL = "sqlite:///./wordpress_mcp.db"

# Создаем движок
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

print("База данных инициализирована успешно!")
