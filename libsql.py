import sqlite3
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# Initialize the database schema
def initialize_database():
    with open("schema.sql", "r") as f:
        cursor.executescript(f.read())
    conn.commit()

# Display available books
def display_available_books():
    cursor.execute("SELECT * FROM Books WHERE status = 'available'")
    books = cursor.fetchall()
    if books:
        print("\nAvailable Books:")
        for book in books:
            print(f"♦ {book[1]}")
    else:
        print("\nNo books available.")

# Borrow a book
def borrow_book(user_name, book_title):
    cursor.execute("SELECT id FROM Users WHERE name = ?", (user_name,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO Users (name) VALUES (?)", (user_name,))
        conn.commit()
        user = (cursor.lastrowid,)

    cursor.execute("SELECT * FROM Books WHERE title = ? AND status = 'available'", (book_title,))
    book = cursor.fetchone()

    if not book:
        print(f"\n{book_title} is not available.\n")
    else:
        cursor.execute("INSERT INTO BorrowTrack (user_id, book_id) VALUES (?, ?)", (user[0], book[0]))
        cursor.execute("UPDATE Books SET status = 'borrowed' WHERE id = ?", (book[0],))
        conn.commit()
        print(f"\nBook '{book_title}' issued to {user_name}.\n")

# Return a book
def return_book(user_name, book_title):
    cursor.execute("""
        SELECT BorrowTrack.id FROM BorrowTrack
        INNER JOIN Users ON BorrowTrack.user_id = Users.id
        INNER JOIN Books ON BorrowTrack.book_id = Books.id
        WHERE Users.name = ? AND Books.title = ? AND Books.status = 'borrowed'
    """, (user_name, book_title))
    track = cursor.fetchone()

    if not track:
        print(f"\nNo record found for {user_name} borrowing '{book_title}'.\n")
    else:
        cursor.execute("DELETE FROM BorrowTrack WHERE id = ?", (track[0],))
        cursor.execute("UPDATE Books SET status = 'available' WHERE title = ?", (book_title,))
        conn.commit()
        print(f"\nBook '{book_title}' returned by {user_name}.\n")

# Main Menu
if __name__ == "_main_":
    initialize_database()

    print("\n♦♦♦ Welcome to the Library System ♦♦♦")
    while True:
        print("\n1. Display Available Books")
        print("2. Borrow Book")
        print("3. Return Book")
        print("4. Exit")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            display_available_books()
        elif choice == "2":
            name = input("Enter your name: ")
            title = input("Enter the book title: ")
            borrow_book(name, title)
        elif choice == "3":
            name = input("Enter your name: ")
            title = input("Enter the book title: ")
            return_book(name, title)
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice! Please try again.")