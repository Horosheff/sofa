#!/usr/bin/env python3
"""
Script to completely reset the database
ВНИМАНИЕ: Удаляет ВСЕ данные!
"""

import sqlite3
import sys
from pathlib import Path

# Path to database
DB_PATH = Path(__file__).parent / "app.db"

def reset_database():
    """Полная очистка базы данных"""
    
    if not DB_PATH.exists():
        print(f"База данных не найдена: {DB_PATH}")
        sys.exit(1)
    
    print(f"ВНИМАНИЕ! Сейчас будут удалены ВСЕ данные из базы данных!")
    print(f"Путь к БД: {DB_PATH}")
    
    response = input("\nВы уверены? Введите 'YES' для подтверждения: ")
    if response != "YES":
        print("Отменено.")
        sys.exit(0)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("\nУдаление всех данных...")
        
        # Удаляем данные из таблиц (но оставляем структуру)
        cursor.execute("DELETE FROM activity_logs")
        print("✓ Очищена таблица activity_logs")
        
        cursor.execute("DELETE FROM admin_logs")
        print("✓ Очищена таблица admin_logs")
        
        cursor.execute("DELETE FROM login_attempts")
        print("✓ Очищена таблица login_attempts")
        
        cursor.execute("DELETE FROM user_settings")
        print("✓ Очищена таблица user_settings")
        
        cursor.execute("DELETE FROM users")
        print("✓ Очищена таблица users")
        
        # Сбрасываем счётчики autoincrement
        cursor.execute("DELETE FROM sqlite_sequence")
        print("✓ Сброшены счётчики ID")
        
        conn.commit()
        print("\n✅ База данных полностью очищена!")
        print("\nТеперь можно начать с чистого листа.")
        print("Первая регистрация создаст нового пользователя с ID=1")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Ошибка при очистке: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    reset_database()

