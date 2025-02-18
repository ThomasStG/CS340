import sqlite3


def connectDB():
    connection = sqlite3.connect("./data.db")
    cursor = connection.cursor()
    # Create a table
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS 
            items (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                size TEXT, 
                isMetric INTEGER, 
                location TEXT, 
                count INTEGER, 
                threshold INTEGER, 
                isContacted INTEGER
            )"""
    )
    return connection, cursor


def findByName(name, isMetric, size, cursor):
    cursor.execute(
        """
        SELECT id FROM items 
        WHERE name = ? AND isMetric = ? AND size = ? 
        """,
        (name, isMetric, size),
    )
    item = cursor.fetchone()  # Fetch the first matching row

    return item[0] if item else None  # Return ID if found, otherwise None


def getItem(itemID, cursor):
    cursor.execute(
        """SELECT 
            name, 
            isMetric, 
            size,
            location, 
            count, 
            threshold, 
            isContacted 
        FROM items 
            WHERE id = ?""",
        (itemID,),
    )
    cursor.row_factory = sqlite3.Row  # This makes fetch results act like dicts
    item = cursor.fetchone()

    return dict(item) if item else None  # Convert Row to a dictionary


def incrementItem(itemID, numAdded, cursor, connection):
    item = getItem(itemID, cursor)
    newCount = item["count"] + numAdded
    isContacted = 1
    if newCount > item["threshold"]:
        isContacted = 0
    cursor.execute(
        """UPDATE items SET count = ?, isContacted = ? WHERE id = ?""",
        (
            newCount,
            isContacted,
            itemID,
        ),
    )

    connection.commit()


def decrimentItem(itemID, numRemoved, cursor, connection):
    item = getItem(itemID, cursor)
    newCount = item["count"] - numRemoved
    newCount = max(newCount, 0)
    cursor.execute(
        """UPDATE items SET count = ? WHERE id = ?""",
        (
            newCount,
            itemID,
        ),
    )
    connection.commit()
    if newCount < int(item["threshold"]) and not item["isContacted"]:
        print("ERROR")
        cursor.execute(
            """
                       UPDATE items SET isContacted = 1 WHERE id = ?
                       """,
            (itemID,),
        )


def addItem(name, size, isMetric, location, count, threshold, cursor, connection):
    cursor.execute(
        """
                   INSERT INTO items
                   (name, size, isMetric, location, count, threshold, isContacted)
                   VALUES
                    (?,?,?,?,?,?,?)
                   """,
        (name, size, isMetric, location, count, threshold, 0),
    )
    connection.commit()


def removeItem(itemID, cursor, connection):
    cursor.execute(
        """
                    DELETE FROM items WHERE id = ?
                   """,
        (itemID,),
    )
    connection.execute()


# print(getItem(1, cur))
# cur.execute("""SELECT * FROM items""")
# print(cur.fetchall())
# incrementItem(1, 4, cur, con)
# print(getItem(1, cur))
# decrimentItem(1, 8, cur, con)
