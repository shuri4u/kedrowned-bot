import sqlite3
import random


libraryDB = sqlite3.connect("library.db")
cursor = libraryDB.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS books"
               "(book_id INTEGER, "
               "title TEXT, "
               "author TEXT,"
               "year INTEGER, "
               "avaible INTEGER DEFAULT 1)")

cursor.execute("CREATE TABLE IF NOT EXISTS readers"
               "(reader_id INTEGER, "
               "name TEXT, "
               "phone TEXT,"
               "book_id INTEGER)")

libraryDB.commit()
libraryDB.close()


id = random.randint(100, 999)

def add_book(id, title, author, year):
    booksDB = sqlite3.connect("library.db")
    cursor = booksDB.cursor()
    id = random.randint(000, 999)

    cursor.execute("INSERT INTO books (book_id, title, author, year)"
                   "VALUES (?,?,?,?)", (id, title, author, year))

    booksDB.commit()
    booksDB.close()

# add_book(id, "Огонь и лёд", "Эрин Хантер", 2003)
# add_book(id, "Лес секретов", "Эрин Хантер", 2004)
# add_book(id, "Бушующая стихия", "Эрин Хантер", 2004)
# add_book(id, "Опасная тропа", "Эрин Хантер", 2004)

def add_reader(id, name, phone):
    libraryDB = sqlite3.connect("library.db")
    cursor = libraryDB.cursor()
    id = random.randint(000, 999)

    cursor.execute("INSERT INTO readers (reader_id, name, phone)"
                   "VALUES (?,?,?)", (id, name, phone))

    libraryDB.commit()
    libraryDB.close()


# add_reader(id, "Нян Кет", "12345")
# add_reader(id, "Дровнед", "67890")
# add_reader(id, "Фурри", "13579")
# add_reader(id, "Татьяна", "24680")


def give_book(reader_id, book_id):
    libraryDB = sqlite3.connect("library.db")
    cursor = libraryDB.cursor()

    cursor.execute("UPDATE books SET avaible=? WHERE book_id=?", (0, book_id))
    cursor.execute("UPDATE readers SET book_id=? WHERE reader_id=?", (book_id, reader_id))

    libraryDB.commit()
    libraryDB.close()

# give_book(556, 935)

def return_book(book_id):
    libraryDB = sqlite3.connect("library.db")
    cursor = libraryDB.cursor()

    cursor.execute("UPDATE books SET avaible=? WHERE book_id=?", (1, book_id))
    cursor.execute("UPDATE readers SET book_id=? WHERE book_id=?", ("null", book_id,))

    libraryDB.commit()
    libraryDB.close()

# return_book(935)

def get_avaible_books():
    booksDB = sqlite3.connect("library.db")
    cursor = booksDB.cursor()
    books = cursor.execute("SELECT * FROM books WHERE avaible = 1")
    print("Список книг:")
    for book in books:
        print(book)

    books = cursor.fetchall()
    booksDB.close()
    return books

get_avaible_books()

def get_reader_books(reader_id):
    pass

def search_books(keyword):
    libraryDB = sqlite3.connect("library.db")
    cursor = libraryDB.cursor()

    search = int(input("1. поиск по названию\n"
                       "2. поиск по автору\n"
                       "выбор: "))
    match search:
        case 1:
            searchh = cursor.execute("SELECT * from books WHERE title=?", (keyword,))
            for book in searchh:
                print("книга: ", book)
        case 2:
            searchh = cursor.execute("SELECT * from books WHERE author=?", (keyword,))
            for book in searchh:
                print("книга: ", book)

    libraryDB.close()

# search_books("Огонь и лёд")
