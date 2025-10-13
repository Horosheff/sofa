#!/usr/bin/env python3
"""
Инициализация базы данных для WordPress MCP Platform
Создает все необходимые таблицы и индексы
"""

import os
import sys
import asyncio
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.database import Base
from app.models import User, UserSettings

async def init_database():
    """Инициализация базы данных"""
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    print(f"🔗 Подключаемся к базе: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL, echo=False)
    
    try:
        print("📋 Создаем таблицы...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ База данных инициализирована!")
        print("✅ Таблицы созданы: users, user_settings")
        
        # Проверяем созданные таблицы
        with engine.connect() as conn:
            result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
            tables = result.fetchall()
            print("📊 Созданные таблицы:")
            for table in tables:
                print(f"  - {table[0]}")
                
        print("🎉 Инициализация завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_database())