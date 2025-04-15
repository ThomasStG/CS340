import hashlib
import os
import sqlite3

from app import get_db, change_pass
from auth import change_password


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

    connection = get_db()
    cursor = connection.cursor()

    username = "admin"
    new_password = "password"
    level = 0
    change_password(username, new_password, level, cursor, connection)
