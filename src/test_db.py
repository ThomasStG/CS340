import sqlite3

connection = sqlite3.connect("../data/data.db")
cursor = connection.cursor()
cursor.execute(
    """
        select * from items
        """
)
print(cursor.fetchall())
connection.commit()
connection.close()
