import logging
import sqlite3

from database import cursor, conn

async def addNewBook(title: str, author: str, description: str, genre_name: str) -> bool:
    """
    Добавляет книгу в базу данных по параметрам title, author, description, genre_name

    :param title: Название книги
    :param author: Автор книги
    :param description: Описание книги
    :param genre_name: Имя жанра
    """
    try:
        cursor.execute('SELECT id FROM genres WHERE name = ?', (genre_name,))
        genre = cursor.fetchone()
    except sqlite3.Error as e:
        return logging.error(f"Ошибка получения ID жанра по имени: {genre_name}\n{e}")

    if not genre:
        """"
        Если жанр отсутствует, то мы его добавим в таблицу genres с полем name
        """

        cursor.execute('INSERT INTO genres (name) VALUES (?)', (genre_name,))
        conn.commit()

        cursor.execute('SELECT id FROM genres WHERE name = ?', (genre_name,))
        genre = cursor.fetchone()

    """
    Добавим запись в таблицу books, заполнив данными, также, взял уже ID жанра
    """
    try:
        cursor.execute('INSERT INTO books (title, author, description, genre_id) VALUES (?, ?, ?, ?)',
                     (title, author, description, genre[0]))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Ошибка создания новой книги: {e}")
        return False
    
async def removeBook(title: str, author: str) -> bool:
    """
    Удаляет книгу из базы данных по названию и автору.
    
    :param title: Название книги для удаления.
    :param author: Автор книги для удаления.
    :return: Возвращает True, если книга была успешно удалена, иначе False.
    """
    try:
        cursor.execute('DELETE FROM books WHERE title = ? AND author = ?', (title, author))

        if cursor.rowcount == 0:
            return False
        
        conn.commit()
        return True 
        
    except sqlite3.Error as e:
        logging.error(f"Ошибка при удалении книги: {e}")
        return False