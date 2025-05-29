import sqlite3

from utility_functions import get_db, import_csv_el

connection = sqlite3.connect("../data/data.db")
connection.row_factory = sqlite3.Row  # Allows dictionary-like row access
cursor = connection.cursor()
cursor.execute(
    """
    DROP TABLE IF EXISTS electrical_active_items
    """
)
connection.commit()
