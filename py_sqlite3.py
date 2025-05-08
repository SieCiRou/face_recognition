"""
SQLite3 create database and table example.
This script creates a SQLite3 database and a table named 'memership' with the following columns:

Keyword arguments:
argument -- description
Return: return_description
"""


import sqlite3

# 資料庫檔案名稱
DATABASE_FILE = 'memership_database.db'

def create_database():
    """建立員工資料庫和資料表."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # 建立 employees 資料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memership (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memership_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                face_encoding BLOB
            )
        ''')

        conn.commit()
        print(f"資料庫 '{DATABASE_FILE}' 和 'memership' 資料表建立成功。")

    except sqlite3.Error as e:
        print(f"資料庫操作錯誤: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()