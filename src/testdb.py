import hashlib
import os
import sqlite3

from auth import ensure_table

with sqlite3.connect("../data/data.db") as connection:
    cursor = connection.cursor()
    cursor.execute("DROP TABLE users")
    connection.commit()


with sqlite3.connect("../data/data.db") as connection:
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
    cursor = connection.cursor()

    username = "admin"
    password = "password"
    salt = os.urandom(32)

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the salt and password
    hash_object.update(salt + password.encode("utf-8"))

    # Get the hashed password as a hexadecimal string
    hashed_password = hash_object.hexdigest()
    cursor.execute(
        "INSERT INTO users (username, password, salt, level) VALUES (?, ?, ?, ?)",
        (username, hashed_password, salt.hex(), 0),
    )
    cursor.execute("SELECT * FROM users")
    connection.commit()
    print(cursor.fetchall())
