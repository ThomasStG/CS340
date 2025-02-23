import sqlite3

from fuzzywuzzy import fuzz, process


def buildDB():
    connection = sqlite3.connect("./data.db")
    cursor = connection.cursor()
    # Create a table
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS 
            items (
                id INTEGER PRIMARY KEY, 
                name TEXT NOT NULL, 
                size TEXT NOT NULL, 
                isMetric INTEGER NOT NULL, 
                location TEXT NOT NULL, 
                count INTEGER NOT NULL, 
                threshold INTEGER NOT NULL, 
                isContacted INTEGER NOT NULL
            )"""
    )
    connection.commit()
    connection.close()


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


def fzf(name, isMetric, size, cursor, top_n=5):
    cursor.row_factory = sqlite3.Row  # Fetch results as dictionaries
    cursor.execute(
        """
        SELECT id, name, isMetric, size, location, count, threshold, isContacted 
        FROM items WHERE isMetric = ?
        """,
        (isMetric,),
    )
    data = cursor.fetchall()  # List of sqlite3.Row (dictionary-like)

    if not data:
        return []  # Return empty list if no data exists

    # Convert rows to dictionaries
    row_dict = {row["id"]: dict(row) for row in data}

    # Create a dictionary {id: "name size"} for fuzzy matching
    choices = {row["id"]: f"{row['name']} {row['size']}" for row in data}

    # Query string to match against
    query = f"{name} {size}"

    # Get top N matches (IDs retained)
    best_matches = process.extract(
        query, choices, scorer=fuzz.partial_ratio, limit=top_n
    )

    # Extract full rows as dictionaries
    results = [row_dict[match[2]] for match in best_matches]  # match[2] is ID

    return results  # List of dictionaries


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


def decrementItem(itemID, numRemoved, cursor, connection):
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
    connection.commit()


# print(getItem(1, cur))
# cur.execute("""SELECT * FROM items""")
# print(cur.fetchall())
# incrementItem(1, 4, cur, con)
# print(getItem(1, cur))
# decrementItem(1, 8, cur, con)
