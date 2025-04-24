from auth import *
import os
import hashlib
import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

salt = os.urandom(16)
password = b"password"
hash_object = hashlib.sha256()
hash_object.update(salt + password)
hashed_password = hash_object.hexdigest()

create_account("admin", 0, hashed_password, salt, cursor, connection)
