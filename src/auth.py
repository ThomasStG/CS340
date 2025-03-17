import sqlite3


def ensure_table():
    """
    Ensures the user table exists in the database

    Args:
        None

    Returns:
        None
    """
    with sqlite3.connect("../data/data.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    salt TEXT NOT NULL
                )
                """
        )
        connection.commit()


def login(username: str, password: str, salt: str, cursor: sqlite3.Cursor) -> bool:
    """
    Attempts to log the user in

    Args:
        username (str): the username of the user
        password (str): the hashed password of the user
        salt (str): the salt of the user
        cursor (sqlite3.Cursor): the cursor to the database

    Returns:
        bool: whether the login was successful
    """
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ? AND salt = ?",
        (username, password, salt),
    )
    return cursor.fetchone() is not None


def create_account(
    username: str,
    password: str,
    salt: str,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    Creates a new user account

    Args:
        username (str): the username of the user
        password (str): the hashed password of the user
        salt (str): the salt of the user
        cursor (sqlite3.Cursor): the cursor to the database
        connection (sqlite3.Connection): the connection to the database

    Returns:
        None
    """
    cursor.execute(
        "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
        (username, password, salt),
    )
    connection.commit()


def change_password(
    username: str,
    old_password: str,
    new_password: str,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    Changes the password of a user

    Args:
        username (str): the username of the user
        old_password (str): the old password of the user
        new_password (str): the new password of the user
        cursor (sqlite3.Cursor): the cursor to the database
        connection (sqlite3.Connection): the connection to the database

    Returns:
        None
    """
    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ? AND password = ?",
        (new_password, username, old_password),
    )
    connection.commit()


def get_salt(username: str, cursor: sqlite3.Cursor) -> str:
    """
    Returns the salt of a user

    Args:
        username (str): the username of the user
        cursor (sqlite3.Cursor): the cursor to the database

    Returns:
        str: the salt of the user
    """
    cursor.execute("SELECT salt FROM users WHERE username = ?", (username,))
    return cursor.fetchone()[0]
