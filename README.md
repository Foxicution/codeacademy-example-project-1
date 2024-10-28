# Task description:

Imagine that you are required to create a simple library management python
program. The program should be able to perform the following functions:

- [x] Add a new book to the library (the book should have at least an author, a
      name, release year and genre)
- [x] It should be possible to remove old/unused books, can be done using
      release year, if older than x, remove
- [x] Readers should be able to borrow a book (the number of books is limited)
- [ ] It should be possible to search for books, using the name of the book, or
      the author
- [ ] The books can be borrowed for a limited amount of time. If the books are
      not returned until the date of return, they are considered overdue.
- [ ] It should be possible to see all the books in the library
- [ ] It should be possible to see all the books that are late
- [ ] It should not be possible to take a book, if the reader has a book that is
      late, and he should be notified, that he has book that is late

## Additional instructions (for bonus points):

- [ ] It should be possible to take the books only using a reader card, and it
      should be possible to register a card and assign it to a reader
- [ ] It should be possible to derrive statistics, of what is the mean late book
      amount and other relevant indicators, such as which genre books are the
      most common, which genre of books are most commonly borrowed, etc.
- [ ] Two roles, Librarian and Reader. The Librarian connects using their
      username and passowrd, and the Reader, using their Reader card number. The
      Reader can't add/remove books.
- [ ] Run the program using streamlit
- [ ] Using a virtual environment for the whole project (both `venv` and
      `poetry` are fine)
- [ ] Could try making a GUI using `tkinter`

## Mandatory requirements:

- A minimal structure should be held (no writing to a single file)
- The program should work, until it is turned off, by the user
- Added/Removed books should be saved between different runs of the program
- Information should be saved using `pkl`/`csv`/`json`/`txt` files
- The program cannot crash (every place where it crashes results in minus
  points)
- All the logic should be in functions/methods/classes. They can be called
  globally, but all the calculations should be in these structures
- It is required to host the codebase on GitHub. Each commit should have a
  rational naming, there should be at least 3 branches and at least 5 commits
  (each commit should be small, and encompass only a single functionality)
