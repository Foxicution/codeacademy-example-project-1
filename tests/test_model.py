from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from proj.model import Book, Borrow, Err, Model, Ok, Reader


@pytest.fixture
def library_model():
    model = Model()

    book1 = Book(
        title="Sample book 1",
        author="Author 1",
        year=datetime(2020, 1, 1),
        genres=["Fiction", "Adventure"],
        copies=2,
    )
    book2 = Book(
        title="Sample Book 2",
        author="Author 2",
        year=datetime(2021, 1, 1),
        genres=["Non-Fiction"],
        copies=1,
    )

    model.add_book(book1)
    model.add_book(book2)

    reader = Reader(name="Sample Reader")
    model.add_reader(reader)

    return model, book1, book2, reader


def test_add_reader(library_model):
    model, _, _, _ = library_model
    new_reader = Reader("Unique Reader")

    result = model.add_reader(new_reader)
    assert isinstance(result, Ok)
    assert new_reader.id in model.readers

    duplicate_result = model.add_reader(new_reader)
    assert isinstance(duplicate_result, Err)


def test_add_book(library_model):
    model, _, _, _ = library_model
    new_book = Book(
        title="Unique Book",
        author="Author Unique",
        year=datetime(2019, 1, 1),
        genres=["Science Fiction"],
    )

    result = model.add_book(new_book)
    assert isinstance(result, Ok)
    assert new_book.id in model.books

    duplicate_result = model.add_book(new_book)
    assert isinstance(duplicate_result, Err)


def test_borrow_book(library_model):
    model, book1, book2, reader = library_model
    due_date = datetime.now() + timedelta(days=7)

    result = model.borrow_book(book1.id, reader.id, due_date)
    assert isinstance(result, Ok)
    assert model.books[book1.id].copies == 1

    result_second_borrow = model.borrow_book(book1.id, reader.id, due_date)
    assert isinstance(result_second_borrow, Ok)
    assert model.books[book1.id].copies == 0

    no_copies_result = model.borrow_book(book1.id, reader.id, due_date)
    assert isinstance(no_copies_result, Err)
    assert "No more copies left for book " in no_copies_result

    overdue_borrow = Borrow(book1.id, reader.id, datetime.now() - timedelta(days=1))
    model.borrows[overdue_borrow.id] = overdue_borrow
    overdue_result = model.borrow_book(book2.id, reader.id, due_date)
    assert isinstance(overdue_result, Err)
    assert "Reader has an overdue borrow of a book " in overdue_result


def test_return_book(library_model):
    model, book1, _, reader = library_model
    due_date = datetime.now() + timedelta(days=7)

    borrow_result = model.borrow_book(book1.id, reader.id, due_date)
    assert isinstance(borrow_result, Ok)
    borrow_id = next(iter(model.borrows))

    return_result = model.return_book(borrow_id)
    assert isinstance(return_result, Ok)
    assert model.books[book1.id].copies == 2

    non_existant_return = model.return_book(uuid4())
    assert isinstance(non_existant_return, Err)


def test_remove_books_by_year(library_model):
    model, book1, book2, reader = library_model
    due_date = datetime.now() + timedelta(days=7)

    model.borrow_book(book1.id, reader.id, due_date)

    remove_result = model.remove_books_by_year(datetime(2019, 12, 31))
    assert isinstance(remove_result, Ok)
    assert book1.id in model.books

    remove_result = model.remove_books_by_year(datetime(2020, 12, 31))
    assert isinstance(remove_result, Ok)
    assert book1.id not in model.books
    assert book2.id in model.books


def test_auth_librarian(library_model):
    model, _, _, _ = library_model

    result = model.add_librarian("admin", "password")
    assert isinstance(result, Ok)

    auth_result = model.auth_librarian("admin", "password")
    assert isinstance(auth_result, UUID)
    assert auth_result in model.sessions

    failed_auth_result = model.auth_librarian("admin", "wrongpassword")
    assert isinstance(failed_auth_result, Err)
    assert "No librarian matching the username and password found" in failed_auth_result


def test_auth_reader(library_model):
    model, _, _, reader = library_model

    auth_result = model.auth_reader(reader.id)
    assert isinstance(auth_result, UUID)
    assert auth_result in model.sessions

    fake_card_id = uuid4()
    failed_auth_result = model.auth_reader(fake_card_id)
    assert isinstance(failed_auth_result, Err)
    assert "No reader found with this card number" in failed_auth_result


def test_validate_session(library_model):
    model, _, _, reader = library_model

    session_id = model.auth_reader(reader.id)
    assert isinstance(session_id, UUID)

    valid_session = model.validate_session(session_id)
    assert valid_session == reader

    model.sessions[session_id].expiration = datetime.now() - timedelta(minutes=1)
    expired_session = model.validate_session(session_id)
    assert isinstance(expired_session, Err)
    assert "Session is expired" in expired_session

    invalid_session = model.validate_session(uuid4())
    assert isinstance(invalid_session, Err)
    assert "Session is invalid" in invalid_session


def test_cleanup_sessions(library_model):
    model, _, _, reader = library_model

    session_id_1 = model.auth_reader(reader.id)
    session_id_2 = model.auth_reader(reader.id)
    model.sessions[session_id_2].expiration = datetime.now() - timedelta(minutes=1)

    assert session_id_1 in model.sessions
    assert session_id_2 in model.sessions

    model.cleanup_sessions()
    assert session_id_1 in model.sessions
    assert session_id_2 not in model.sessions
