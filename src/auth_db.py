"""
This module provides functions for interacting with an
SQLite database for a user authentication and management system.
It includes functions to:
    - Ensure the user table exists in the database
    - Generate and verify login tokens
    - Log in a user
    - Create a new user account
    - Change a user's password or access level
    - Fetch salts for hashing
    - List users
    - Delete users
"""

import datetime
import hashlib
import os
import sqlite3

import jwt
from dotenv import load_dotenv


def ensure_table():
    """
    Ensures the user table exists in the database

    Args:
        None

    Returns:
        None
    """
    with sqlite3.connect("data/data.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    token TEXT,
                    level INTEGER NOT NULL
                )
                """
        )
        connection.commit()
        connection.close()


def generate_token(username: str, level: int):
    """
    Generates a JWT token for the user

    Args:
        username (str): the username of the user
        level (int): the level of the user

    Returns:
        str: the JWT token
    """
    load_dotenv("../data/.env")
    SECRET_KEY = os.environ.get("Login_Token_Secret_Key")
    payload = {
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=30),
        "username": username,
        "level": level,
    }
    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        print(f"JWT encoding error: {e}")
        raise


def login(
    username: str, password: str, cursor: sqlite3.Cursor, connection: sqlite3.Connection
) -> str:
    """
    Attempts to log the user in by checking credentials, and generates a token.

    Args:
        username (str): The username of the user.
        password (str): The hashed password of the user.
        cursor (sqlite3.Cursor): The cursor to the database.
        connection (sqlite3.Connection): The connection to the database.

    Returns:
        str: The login token if successful, otherwise an empty string.
    """
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    )
    output = cursor.fetchone()
    if output is None:
        return ""
    token = generate_token(username, output[5])
    cursor.execute(
        "UPDATE users SET token = ? WHERE username = ?",
        (token, username),
    )
    connection.commit()
    return token


def check_token(token: str, username: str, cursor: sqlite3.Cursor) -> bool:
    """
    Checks if the user is logged in

    Args:
        token (str): the token of the user
        username (str): the username of the user
        cursor (sqlite3.Cursor): the cursor to the database

    Returns:
        bool: whether the user is logged in
    """
    cursor.execute(
        "SELECT token FROM users WHERE username = ?",
        (username,),
    )
    old_token = cursor.fetchone()[0]
    if old_token and old_token != token:
        return False
    return True


def create_account(
    username: str,
    level: int,
    password: str,
    salt: str,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    Creates a new user account

    Args:
        username (str): the username of the user
        level (int): the access level of the user
        password (str): the hashed password of the user
        salt (str): the salt of the user
        cursor (sqlite3.Cursor): the cursor to the database
        connection (sqlite3.Connection): the connection to the database

    Returns:
        None
    """
    cursor.execute(
        "INSERT INTO users (username, level, password, salt) VALUES (?, ?, ?, ?)",
        (username, level, password, salt),
    )
    connection.commit()


def change_password(
    username: str,
    new_password: str,
    level: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    Changes a user's password and/or access level.

    If a new password is provided, it will be hashed and updated along with the level.
    If the new password is empty, only the access level is updated.

    Args:
        username (str): The username of the user.
        new_password (str): The new password of the user (empty string if only changing level).
        level (int): The new access level of the user.
        cursor (sqlite3.Cursor): The cursor to the database.
        connection (sqlite3.Connection): The connection to the database.

    Returns:
        None
    """
    if new_password == "":
        cursor.execute(
            "UPDATE users SET level = ? WHERE username = ?",
            (level, username),
        )
    else:
        cursor.execute("SELECT salt FROM users WHERE username = ?", (username,))
        salt = cursor.fetchone()[0]
        hash_object = hashlib.sha256()
        hash_object.update(salt.encode("utf-8") + new_password.encode("utf-8"))
        new_password_hash = hash_object.hexdigest()
        cursor.execute(
            "UPDATE users SET password = ?, level = ? WHERE username = ?",
            (new_password_hash, level, username),
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


def get_users(cursor: sqlite3.Cursor) -> list[dict]:
    """
    fetches all users' usernames and levels.

    args:
        cursor (sqlite3.cursor): the cursor to the database.

    returns:
        list[dict]: a list of dictionaries with 'username' and 'level' keys.
    """
    cursor.execute("SELECT username, level FROM users")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]  # Convert Row to dict


def delete_user(username: str, cursor: sqlite3.Cursor, connection: sqlite3.Connection):
    """
    Deletes a user from the database.

    Args:
        username (str): The username of the user to delete.
        cursor (sqlite3.Cursor): The cursor to the database.
        connection (sqlite3.Connection): The connection to the database.

    Returns:
        None
    """
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    connection.commit()


if __name__ == "__main__":
    pass
