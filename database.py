import sqlite3
import shutil
import os
from datetime import datetime

DB_NAME = "budget_goals.db"

def get_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Creates tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Income Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT
        )
    ''')
    
    # Expenses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            description TEXT,
            notes TEXT
        )
    ''')
    
    # Savings Goals Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL NOT NULL,
            deadline TEXT NOT NULL,
            notes TEXT
        )
    ''')
    
    # Budget Planner Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL, -- Format: YYYY-MM
            category TEXT NOT NULL,
            allocated_amount REAL NOT NULL,
            UNIQUE(month, category)
        )
    ''')
    
    conn.commit()
    conn.close()

def backup_database(dest_path):
    """Backs up the current database file to a safe location."""
    if os.path.exists(DB_NAME):
        shutil.copy2(DB_NAME, dest_path)
        return True
    return False

def restore_database(src_path):
    """Restores the database from a backup file."""
    if os.path.exists(src_path):
        shutil.copy2(src_path, DB_NAME)
        return True
    return False