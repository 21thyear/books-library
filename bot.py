import asyncio
import logging
import sys
import os

from database import *

from search_manager import getBooks, getBookInfo, findBooksByDetails, findBookByKeyword
from book_manager import addNewBook, removeBook
from utils import get_genres

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types

from aiogram.filters import CommandStart, Command
from aiogram import F

from aiogram.types import Message


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

async def main() -> None:
    await createTables()
    await dp.start_polling(bot)

@dp.message(CommandStart())
async def onStartCommandHandler(message: Message) -> None:
    return await message.answer("Добро пожаловать в библиотеку, используйте команды:\n\n/books - просмотреть список всех книг\n/about [Название] [автор]\n/find [часть]\n/deletebook\n/keyboard [ключевое слово/фраза] - поиск книги\n/newbook - добавить книгу\nУзнать об книге: /about название;автор")

@dp.message(Command("books"))
async def onBooksCommandHandler(message: Message):
    """
    Попробуем получить список всех книг, в случае проблемы(ошибки), сообщим об этом.
    Есть книги есть, то вернем пользователю строку формата название:автор
    """
    try:
        books = await getBooks()
    except Exception as e:  
        logging.error(f"Ошибка получения списка книг: {e}")
        return await message.reply("Ошибка получения списка книг")
    
    if not books:
        return await message.reply("Список книг пуст.")

    books_data = [f"Название: {book[1]}. Автор: {book[2]}" for book in books]
    books_formatted_message = "\n".join(books_data)
    await message.reply(f"Список книг:\n\n{books_formatted_message}")

@dp.message(Command("newbook"))
async def onNewBookCommandHandler(message: types.Message):
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        existing_genres = await get_genres()
        genre_list = ', '.join(existing_genres)

        return await message.reply(
            "Формат: /newbook Название; Автор; Описание; Жанр\n\n"
            "Доступные жанры: " + genre_list + "\n"
            "Если вашего жанра нет в списке, просто введите его."
        )

    book_data = args[1].split(';')
    if len(book_data) != 4:
        return await message.reply("Формат: /newbook Название; Автор; Описание; Жанр")

    title, author, description, genre = [data.strip() for data in book_data]

    if await addNewBook(title, author, description, genre):
        return await message.reply("Книга успешно добавлена!")
    else:
        return await message.reply("Ошибка при добавлении книги!")

@dp.message(Command("deletebook"))
async def onNewBookCommandHandler(message: types.Message):
    """
    Обработчик для команды /deletebook.
    """
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.reply("Формат: /deletebook Название; Автор;")

    book_data = args[1].split(';')
    if len(book_data) != 2:
        return await message.reply("Формат: /deletebook Название; Автор;")

    title, author = [param.strip() for param in book_data]
    if await removeBook(title, author):
        return await message.reply("Книга успешно удалена!")
    else:
        return await message.reply("Книга не найдена или произошла ошибка при удалении.")

@dp.message(Command("about"))
async def onEditCommandHandler(message: types.Message):
    """
    Разделим входящую строку команды /about по знаку для разделителя ";", после сверим количество аргументов
    Затем попросим у функции get_book_info вернуть информацию об запросе
    """

    try:
        args = message.text.split(maxsplit=1)
        book_data = args[1].split(';')
    except Exception as e:
        return await message.reply("Пожалуйста, введите данные в формате: /about Название; Автор")

    title, author = [param.strip() for param in book_data]
    
    try:
        book_info = await getBookInfo(title, author)
        if book_info:
            await message.reply(f"Номер книги: {book_info[0]}.\nОписание: {book_info[1]}\nЖанр: {book_info[2]}\n\nДля удаления используйте: /deletebook")
        else:
            await message.reply("Книга не найдена. Пожалуйста, проверьте введенные данные и попробуйте снова.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при поиске книги: {e}")

@dp.message(Command("find"))
async def onFindCommandHandler(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.reply(
            "Введите запрос в формате: /find [название];[автор];[жанр]\n\nДля пропуска аргумента, используйте ;, например, /find ;;Love"
        )

    search_params = args[1].split(';')
    title = search_params[0].strip() if len(search_params) > 0 else None
    author = search_params[1].strip() if len(search_params) > 1 else None
    genre = search_params[2].strip() if len(search_params) > 2 else None

    books = await findBooksByDetails(title, author, genre)
    if books:
        responses = []
        for book in books:
            title, author, genre_name = book
            responses.append(f"Название: {title}, Автор: {author}, Жанр: {genre_name}")
        await message.reply('\n\n'.join(responses))
    else:
        await message.reply("Книги по вашему запросу не найдены.")

@dp.message(Command("keyword"))
async def onKeywordCommandHandler(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.reply("Формат: /keyword [фраза]")

    keyword = args[1].strip()
    
    try:
        books = await findBookByKeyword(keyword) 
        if books:
            responses = []
            for title, author in books:
                responses.append(f"Название: {title}, Автор: {author}")
            await message.reply('\n\n'.join(responses))
        else:
            await message.reply("Книги по вашему запросу не найдены.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при поиске: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
