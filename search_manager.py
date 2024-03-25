from typing import List, Tuple
from database import cursor, conn

import sqlite3
import logging

async def getBooks() -> List[Tuple]:
    try:
        cursor.execute("SELECT id, title, author FROM books")
        books = cursor.fetchall()
        return books
    except sqlite3.DatabaseError as e:
        logging.error(f"Ошибка получения списка книг {e}")
        raise e
    
async def getBookInfo(title: str, author: str) -> List[Tuple]:
    """
    Функция узнает информацию по книге.

    :param title: Название книги
    :param author: Автор книги
    """
    try:
        cursor.execute('''
            SELECT b.id, b.description, g.name 
            FROM books b
            INNER JOIN genres g ON b.genre_id = g.id
            WHERE b.title = ? AND b.author = ?
        ''', (title, author,))
        result = cursor.fetchone()
        return result
    except sqlite3.DatabaseError as e:
        logging.error(f"Ошибка получения информации по книге. {e}")
        raise e
        
async def findBooksByDetails(title: str = None, author: str = None, genre: str = None) -> List[Tuple]:
    """
    Функция узнает книги, по некой информации, полученной от пользователя

    :param title: Название книги
    :param author: Автор книги
    :param genre: Жанр книги
    """
    query = "SELECT b.title, b.author, g.name FROM books b LEFT JOIN genres g ON b.genre_id = g.id WHERE 1=1"
    params = []
    
    if title:
        query += " AND b.title LIKE ?"
        params.append(f"%{title}%")
        
    if author:
        query += " AND b.author LIKE ?"
        params.append(f"%{author}%")
    
    if genre:
        query += " AND g.name LIKE ?"
        params.append(f"%{genre}%")

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Ошибка при поиске книг: {e}")
        return []

async def findBookByKeyword(keyword: str) -> List[Tuple]:
    """
    Функция возвращает название и автора книги, если ключевое слово найдено было в одном из.

    :param keyword: Ключевое слово
    """
    safe_keyword = f"%{keyword}%"

    try:
        cursor.execute('''
            SELECT title, author
            FROM books
            WHERE title LIKE ? OR author LIKE ?
        ''', (safe_keyword, safe_keyword,))
        # Получаем все результаты
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Произошла ошибка при поиске книги: {e}")
        return []