"""
This module provides functions for interacting with an
SQLite database for an inventory management system.
It includes functions to:
    - Ensure the table exists in the database
    - Retrieve all items  Perform fuzzy searching for items
    - Find an item ID based on its identifying information
    - Retrieve a specific item
    - Increment an item's count
    - Decrement an item's count
    - Add a new item
    - Remove an item

Functions:
    build_db() -> None
    get_all(cursor: sqlite3.Cursor) -> list[dict]
    find_by_name(name: str, is_metric: int, size: str, cursor: sqlite3.Cursor) -> int | None
    fzf(name: str, is_metric: int, size: str, cursor: sqlite3.Cursor, top_n: int = 5) -> list[dict]
    get_item(item_id: int, cursor: sqlite3.Cursor) -> list[dict] | None
    increment_item(item_id: int, num_added: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection) -> None
    decrement_item(item_id: int, num_removed: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection) -> int
    add_item(name: str, size: str, is_metric: int, location: str, count: int, threshold: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection) -> None
    remove_item(item_id: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection) -> None

Dependencies:
    `sqlite3`: Built-in Python module for interacting with SQLite databases.
    `fuzzywuzzy`: Library for fuzzy string matching using Levenshtein distance. Install with:
      ```sh
    pip install fuzzywuzzy python-Levenshtein
    ```
    (`python-Levenshtein` is optional but recommended for better performance.)
"""

import csv
import datetime
import glob
import logging
import sqlite3

from fuzzywuzzy import fuzz, process


def build_db() -> None:
    """
    Ensures the table exists in the database
    """
    logger = logging.getLogger(__name__)
    with sqlite3.connect("../data/data.db") as connection:
        cursor = connection.cursor()
        # Create a table
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS 
                items (
                    id INTEGER PRIMARY KEY, 
                    name TEXT NOT NULL, 
                    size TEXT NOT NULL, 
                    is_metric INTEGER NOT NULL, 
                    location TEXT NOT NULL, 
                    count INTEGER NOT NULL, 
                    threshold INTEGER NOT NULL, 
                    isContacted INTEGER NOT NULL DEFAULT 0
                )"""
        )
        connection.commit()


def get_all(cursor: sqlite3.Cursor) -> list[dict]:
    """
    returns all items from the database

    Args:
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries

    Returns:
        list[dict]: list of items in dictionary
    """
    logger = logging.getLogger(__name__)
    cursor.execute(
        """
                   SELECT id, name, is_metric, size, location, count, threshold
                   FROM items
                   """
    )
    items = cursor.fetchall()
    if not items:
        logger.debug("No items found")

    return [
        dict(zip([column[0] for column in cursor.description], row)) for row in items
    ]


def find_by_name(
    name: str, is_metric: int, size: str, cursor: sqlite3.Cursor
) -> int | None:
    """
    returns the id of an object based on its identifying information

    Args:
        name (str): the name of the item to retrieve
        is_metric (int): whether the item is metric (1) or not (0)
        size (str): size string of the object
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries

    Returns:
        int: item id of the object
    """
    logger = logging.getLogger(__name__)
    cursor.execute(
        """
        SELECT id FROM items 
        WHERE name = ? AND is_metric = ? AND size = ? 
        """,
        (name, is_metric, size),
    )
    item = cursor.fetchone()  # Fetch the first matching row

    if not item:
        logger.debug("Item not found")

    return item[0] if item else None  # Return ID if found, otherwise None


def fzf(
    name: str, is_metric: int, size: str, cursor: sqlite3.Cursor, top_n: int = 5
) -> list[dict]:
    """
    finds the 5 most similar items to the input

    Args:
        name (str): the name of the item
        is_metric (int): whether the items are metric (1) or not (0)
        size (str): size string of the object
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        top_n (optional) the number of items to return

    Returns:
        list[dict]: list of json objects
    """
    logger = logging.getLogger(__name__)
    cursor.execute(
        """
        SELECT id, name, is_metric, size, location, count, threshold
        FROM items WHERE is_metric = ?
        """,
        (is_metric,),
    )
    data = cursor.fetchall()

    if not data:
        logger.debug("No items found")
        return []

    # Convert rows to dictionaries
    row_dict = {row["id"]: dict(row) for row in data}

    # Create a dictionary {id: "name size"} for fuzzy matching
    choices = {row["id"]: f"{row['name']} {row['size']}" for row in data}

    # Handle cases where size is empty or None
    query = f"{name} {size}" if size else name

    # Get top N matches with their IDs
    best_matches = process.extract(
        query, choices, scorer=fuzz.partial_ratio, limit=top_n
    )

    # Extract full rows as dictionaries using their IDs
    results = [row_dict[match[2]] for match in best_matches]

    return results  # Return structured output


def get_item(item_id: int, cursor: sqlite3.Cursor) -> list[dict]:
    """
    returns item information from item id

    Args:
        item_id (int): item id to retrieve
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries

    Returns:
        list[dict]: item information as a dict in a list.
    """
    logger = logging.getLogger(__name__)
    cursor.execute(
        """SELECT 
            id,
            name, 
            is_metric, 
            size,
            location, 
            count, 
            threshold, 
            isContacted 
        FROM items 
            WHERE id = ?""",
        (item_id,),
    )
    item = cursor.fetchone()

    if not item:
        logger.debug("Item not found")

    return [dict(item)] if item else None  # Convert Row to a dictionary


def increment_item(
    item_id: int, num_added: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection
) -> None:
    """
    increments an items count by num_added

    Args:
        item_id (int): the item to increment
        num_added (int): the amount to add
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes
    """

    item = get_item(item_id, cursor)  # get items information from id
    new_count = item[0]["count"] + num_added
    is_contacted = 1
    if new_count > item[0]["threshold"]:
        # if the item's count exceeds the threshold, reset the is_contacted status to false
        is_contacted = 0
    # update the database entry with new count and is_contacted values
    cursor.execute(
        """UPDATE items SET count = ?, iscontacted = ? WHERE id = ?""",
        (
            new_count,
            is_contacted,
            item_id,
        ),
    )

    connection.commit()  # save the database


def decrement_item(
    item_id: int,
    num_removed: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> int:
    """
    decrements an item's count by num_removed

    Args:
        item_id (int): the item do decriment
        num_removed (int): the amount to remove
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        int: status code (0/1) for if an email needs to be sent
    """
    item = get_item(item_id, cursor)
    new_count = item[0]["count"] - num_removed
    new_count = max(new_count, 0)
    cursor.execute(
        """update items set count = ? where id = ?""",
        (
            new_count,
            item_id,
        ),
    )
    connection.commit()
    if new_count < int(item[0]["threshold"]) and not item[0]["iscontacted"]:
        cursor.execute(
            """
                       UPDATE items SET iscontacted = 1 WHERE id = ?
                       """,
            (item_id,),
        )
        connection.commit()
        return 1
    return 0


def add_item(
    name: str,
    size: str,
    is_metric: int,
    location: str,
    count: int,
    threshold: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    Adds a new item to the database

    Args:
        name (str): name of the item
        size (str): size of the item
        is_metric (int): whether the item is metric (1) or not (0)
        location (str): the location string of the item
        count (int): the current number of items in stock
        threshold (int): the minimum threshold before ordering more
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes
    """
    cursor.execute(
        """
                   INSERT INTO items
                   (name, size, is_metric, location, count, threshold, iscontacted)
                   VALUES
                    (?,?,?,?,?,?,?)
                   """,
        (name, size, is_metric, location, count, threshold, 0),
    )

    connection.commit()


def remove_item(
    item_id: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection
) -> None:
    """
    deletes an item from the database

    Args:
        item_id (int): item id to delete
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes
    """
    logger = logging.getLogger(__name__)
    cursor.execute(
        """
                    DELETE FROM items WHERE id = ?
                   """,
        (item_id,),
    )
    logger.debug("Item %i removed", item_id)
    connection.commit()


def update_item(
    name: str,
    size: str,
    is_metric: bool,
    location: str,
    threshold: int,
    new_name: str,
    new_size: str,
    new_is_metric: bool,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    updates an item in the database

    Args:
        name (str): name of the item
        size (str): size of the item
        is_metric (int): whether the item is metric (1) or not (0)
        location (str): the location string of the item
        threshold (int): the minimum threshold before ordering more
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    logger = logging.getLogger(__name__)
    item_id = find_by_name(name, is_metric, size, cursor)
    cursor.execute(
        """
                   UPDATE items SET name = ?, size = ?, is_metric = ?, location = ?, threshold = ? WHERE id = ?
                   """,
        (new_name, new_size, new_is_metric, location, threshold, item_id),
    )
    logger.debug("Item %s updated", name)
    connection.commit()


def backup_data(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    # Assuming column names are available in cursor.description
    column_names = [description[0] for description in cursor.description]

    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(date)

    # Open the CSV file for writing
    with open(f"../data/data{date}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=column_names)

        # Write the header (column names)
        writer.writeheader()
        print("header written")

        # Write the rows (data)
        for item in items:
            row = dict(zip(column_names, item))
            writer.writerow(row)
        print(items)


def get_backup_files() -> list[str]:
    return glob.glob("../data/*.csv")


if __name__ == "__main__":
    connection = sqlite3.connect("../data/data.db")
    cursor = connection.cursor()
    # cursor.execute(
    #     """
    #     INSERT INTO items (name, size, is_metric, location, count, threshold, iscontacted)
    #     VALUES
    #     ('test', 'test', 1, '{"shelf": "1", "rack": "1", "box": "1", "height": "1", "width": "1", "depth": "1"}', 1, 1, 0)
    #     """
    # )
    # connection.commit()
    # connection.close()
    cursor.execute(
        """
        SELECT * FROM items
        """
    )
    print(cursor.fetchall())
