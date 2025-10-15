#!/usr/bin/env python3
"""
Миграция базы данных для добавления полей Telegram
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Добавить поля Telegram в таблицу user_settings"""
    
    # Путь к базе данных
    db_path = Path(__file__).parent / "app.db"
    
    if not db_path.exists():
        print("❌ База данных не найдена!")
        return False
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Проверяем, существуют ли уже поля Telegram
        cursor.execute("PRAGMA table_info(user_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        telegram_fields = [
            'telegram_bot_token',
            'telegram_webhook_url', 
            'telegram_webhook_secret'
        ]
        
        # Добавляем поля, если их нет
        for field in telegram_fields:
            if field not in columns:
                print(f"➕ Добавляем поле: {field}")
                cursor.execute(f"ALTER TABLE user_settings ADD COLUMN {field} TEXT")
            else:
                print(f"✅ Поле {field} уже существует")
        
        # Сохраняем изменения
        conn.commit()
        print("✅ Миграция завершена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_database()
