from auth import ensure_table, create_account
import sqlite3
import os
import hashlib

with sqlite3.connect("../data/data.db") as connection:
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
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

    salt = os.urandom(32)

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the salt and password
    hash_object.update(salt + "password".encode("utf-8"))

    # Get the hashed password as a hexadecimal string
    hashed_password = hash_object.hexdigest()

    create_account("admin", 0, hashed_password, salt.hex(), cursor, connection)
    connection.commit()
