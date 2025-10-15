#!/usr/bin/env python3
"""
Migration script for v4.0.0 database schema updates
Adds missing columns to existing database
"""

import sqlite3
import sys
from pathlib import Path

# Path to database
DB_PATH = Path(__file__).parent / "app.db"

def migrate_database():
    """Add missing columns to database"""
    
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
    
    print(f"Migrating database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if is_admin column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("✓ Added is_admin column")
        else:
            print("✓ is_admin column already exists")
        
        # Create admin_logs table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_user_id INTEGER,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (id),
                FOREIGN KEY (target_user_id) REFERENCES users (id)
            )
        """)
        print("✓ admin_logs table ready")
        
        # Create login_attempts table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                ip_address TEXT,
                success BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ login_attempts table ready")
        
        # Create activity_logs table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                action_name TEXT,
                status TEXT DEFAULT 'success',
                details TEXT,
                error_message TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("✓ activity_logs table ready")
        
        # Add missing columns to existing activity_logs table
        cursor.execute("PRAGMA table_info(activity_logs)")
        activity_columns = [row[1] for row in cursor.fetchall()]
        
        if 'action_name' not in activity_columns:
            cursor.execute("ALTER TABLE activity_logs ADD COLUMN action_name TEXT")
            print("✓ Added action_name column to activity_logs")
            
        if 'status' not in activity_columns:
            cursor.execute("ALTER TABLE activity_logs ADD COLUMN status TEXT DEFAULT 'success'")
            print("✓ Added status column to activity_logs")
            
        if 'error_message' not in activity_columns:
            cursor.execute("ALTER TABLE activity_logs ADD COLUMN error_message TEXT")
            print("✓ Added error_message column to activity_logs")
            
        if 'ip_address' not in activity_columns:
            cursor.execute("ALTER TABLE activity_logs ADD COLUMN ip_address TEXT")
            print("✓ Added ip_address column to activity_logs")
            
        if 'user_agent' not in activity_columns:
            cursor.execute("ALTER TABLE activity_logs ADD COLUMN user_agent TEXT")
            print("✓ Added user_agent column to activity_logs")
        
        # Commit changes
        conn.commit()
        print("\n✓ Database migration completed successfully!")
        
        # Show current schema
        cursor.execute("PRAGMA table_info(users)")
        print("\nCurrent users table schema:")
        for row in cursor.fetchall():
            print(f"  - {row[1]} ({row[2]})")
        
    except Exception as e:
        conn.rollback()
        print(f"\nError during migration: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

