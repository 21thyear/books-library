import sqlite3
import asyncio
import logging

try:
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
except sqlite3.DatabaseError as e:
    print(f"Ошибка базы данных: {e}")

async def createTables() -> None:
    try:
        cursor.execute(\
        """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                description TEXT,
                genre_id INTEGER,
                FOREIGN KEY (genre_id) REFERENCES genres (id)
            );
        """)
        conn.commit()

        cursor.execute(\
        """
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Ошибка создания таблицы: {e}")
    finally:
        print(f"Создание таблиц произошло успешно.")