from dataclasses import dataclass, field
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

SESSION_DURATION = timedelta(hours=1)


class Ok(str): ...


class Err(str): ...


@dataclass
class Book:
    title: str
    author: str
    year: datetime
    genres: list[str]
    copies: int = 1
    borrowed: int = 0
    id: UUID = field(default_factory=uuid4)

    def borrow_book(self) -> bool:
        if self.copies > 0:
            self.copies -= 1
            self.borrowed += 1
            return True
        return False

    def return_book(self):
        self.copies += 1
        self.borrowed -= 1

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Book):
            return (
                self.title == other.title
                and self.author == other.author
                and self.year == other.year
            )
        return False


@dataclass
class Borrow:
    book_id: UUID
    reader_id: UUID
    due_date: datetime
    id: UUID = field(default_factory=uuid4)


@dataclass
class Reader:
    name: str
    id: UUID = field(default_factory=uuid4)


class Librarian:
    def __init__(self, username: str, password: str):
        self.id = uuid4()
        self.username = username
        # TODO: Could use a more secure hashing algorithm here
        self.password_hash = sha256(password.encode()).hexdigest()

    def auth(self, password: str) -> bool:
        return self.password_hash == sha256(password.encode()).hexdigest()


class Session:
    def __init__(self, user: Librarian | Reader):
        self.user = user
        self.expiration = datetime.now() + SESSION_DURATION
        self.id = uuid4()


@dataclass
class Model:
    librarians: dict[UUID, Librarian] = field(default_factory=dict)
    readers: dict[UUID, Reader] = field(default_factory=dict)
    books: dict[UUID, Book] = field(default_factory=dict)
    borrows: dict[UUID, Borrow] = field(default_factory=dict)

    sessions: dict[UUID, Session] = field(default_factory=dict)

    def cleanup_sessions(self):
        now = datetime.now()
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if session.expiration < now
        ]
        
        for session in expired_sessions:
            self.sessions.pop(session.id)

    def add_librarian(self, username: str, password: str) -> Ok | Err:
        if any(
            librarian.username == username for librarian in self.librarians.values()
        ):
            return Err(f"Librarian with username: {username} already exists.")

        librarian = Librarian(username, password)
        self.librarians[librarian.id] = librarian
        return Ok(f"Librarian {username} succesfully added.")

    def auth_librarian(self, username: str, password: str) -> UUID | Err:
        librarian = next(
            (
                librarian
                for librarian in self.librarians.values()
                if librarian.username == username and librarian.auth(password)
            ),
            None,
        )
        if librarian is None:
            return Err("No librarian matching the username and password found.")

        session = Session(librarian)
        self.sessions[session.id] = session
        self.cleanup_sessions()
        return session.id

    def add_reader(self, reader: Reader) -> Ok | Err:
        if reader.id in self.readers.keys():
            return Err(f"A reader with id {reader.id} exists.")
        self.readers[reader.id] = reader
        return Ok(
            f"Reader {reader.name} succesfully created. Reader card number: {reader.id.int}"
        )

    def auth_reader(self, reader_id: UUID) -> UUID | Err:
        if reader_id not in self.readers:
            return Err("No reader found with this card number.")

        session = Session(self.readers[reader_id])
        self.sessions[session.id] = session
        self.cleanup_sessions()
        return session.id

    def validate_session(self, session_id: UUID) -> Librarian | Reader | Err:
        if session_id not in self.sessions:
            return Err("Session is invalid")

        session = self.sessions[session_id]
        if datetime.now() > session.expiration:
            self.sessions.pop(session.id)
            return Err("Session is expired")

        return self.sessions[session_id].user

    def add_book(self, book: Book) -> Ok | Err:
        if any(book == existing_book for existing_book in self.books.values()):
            return Err(
                f"A book with a title: {book.title}, author: {book.author},"
                f" year: {book.year} already exists"
            )
        self.books[book.id] = book
        return Ok("The book was inserted succesfully.")

    def remove_books_by_year(self, year: datetime) -> Ok:
        books_to_remove = set(
            book_id for book_id, book in self.books.items() if book.year > year
        )
        borrows_to_remove = [
            borrow_id
            for borrow_id, borrow in self.borrows.items()
            if borrow.book_id in books_to_remove
        ]

        for borrow_id in borrows_to_remove:
            self.borrows.pop(borrow_id)

        for book_id in books_to_remove:
            self.books.pop(book_id)

        return Ok("The books were removed succesfully!")

    def borrow_book(
        self, book_id: UUID, reader_id: UUID, due_date: datetime
    ) -> Ok | Err:
        if self.readers.get(reader_id) is None:
            return Err(f"No reader with id {reader_id}")
        overdue_borrow = next(
            (
                borrow
                for borrow in self.borrows.values()
                if borrow.reader_id == reader_id and borrow.due_date < datetime.now()
            ),
            None,
        )
        if overdue_borrow is not None:
            overdue_book = self.books[overdue_borrow.book_id]
            return Err(f"Reader has an overdue borrow of a book {overdue_book.title}")
        if (book := self.books.get(book_id)) is None:
            return Err(f"No book with id {book_id}")
        if not book.borrow_book():
            return Err(f"No more copies left for book {book.title}")

        borrow = Borrow(book_id, reader_id, due_date)
        self.borrows[borrow.id] = borrow
        return Ok("Book borrowed succesfully")

    def return_book(self, borrow_id: UUID) -> Ok | Err:
        if (borrow := self.borrows.pop(borrow_id, None)) is None:
            return Err(f"A borrow with id {borrow_id} not found")

        self.books[borrow.book_id].return_book()
        return Ok("The book was returned succesfully!")
