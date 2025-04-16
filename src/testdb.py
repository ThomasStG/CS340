import hashlib
import os
import sqlite3

from app import get_db, change_pass
from auth import create_account


def change_pass():
    """
    Handles changing a user's password

    Args:
        username (str): the username of the user
        level str: the cookie of the user
        new_password (str): the new password of the user
        token (str): the token of the user

    Returns:
        json: a message and status code
    """

    connection = sqlite3.connect("../data/data.db")  # get_db()
    cursor = connection.cursor()

    username = "sw"
    password = "password"
    level = 2
    salt = os.urandom(32)

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the salt and password
    hash_object.update(salt + password.encode("utf-8"))

    # Get the hashed password as a hexadecimal string
    hashed_password = hash_object.hexdigest()
    create_account(username, level, hashed_password, salt.hex(), cursor, connection)

    connection.close()


change_pass()
