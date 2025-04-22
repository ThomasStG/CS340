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
                    loc_shelf TEXT NOT NULL, 
                    loc_rack TEXT NOT NULL,
                    loc_box TEXT NOT NULL,
                    loc_row TEXT NOT NULL,
                    loc_col TEXT NOT NULL,
                    loc_depth TEXT NOT NULL,
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
    cursor.execute(
        """
                   SELECT id, name, size, is_metric, loc_shelf,
                   loc_rack, loc_box, loc_row, loc_col, 
                   loc_depth, count, threshold, isContacted
                   FROM items
                   """
    )
    items = cursor.fetchall()

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
    cursor.execute(
        """
        SELECT id FROM items 
        WHERE LOWER(name) = LOWER(?) AND is_metric = ? AND LOWER(size) = LOWER(?) 
        """,
        (name, is_metric, size),
    )
    item = cursor.fetchone()  # Fetch the first matching row
    if item is None:
        raise ValueError("Item not found. No update performed.")

    return item[0] if item else None  # Return ID if found, otherwise None


def fzf(
    name: str, is_metric: int, size: str, cursor: sqlite3.Cursor, top_n: int = 10
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
    cursor.execute(
        """
        SELECT id, name, is_metric, size, loc_shelf, loc_rack, loc_box,
        loc_row, loc_col, loc_depth, count, threshold
        FROM items WHERE is_metric = ?
        """,
        (is_metric,),
    )
    cursor.execute("SELECT * FROM items")
    data = cursor.fetchall()

    if not data:
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
    cursor.execute(
        """SELECT 
            id,
            name, 
            is_metric, 
            size,
            loc_shelf,
            loc_rack,
            loc_box,
            loc_row,
            loc_col,
            loc_depth, 
            count, 
            threshold, 
            isContacted 
        FROM items 
            WHERE id = ?""",
        (item_id,),
    )
    item = cursor.fetchone()

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
    if new_count < int(item[0]["threshold"]) and not item[0]["isContacted"]:
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
    loc_shelf: str,
    loc_rack: str,
    loc_box: str,
    loc_row: str,
    loc_col: str,
    loc_depth: str,
    count: int,
    threshold: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    Adds a new item to the database or updates an existing one by incrementing the count.

    Args:
        name (str): name of the item
        size (str): size of the item
        is_metric (int): whether the item is metric (1) or not (0)
        loc_shelf (str): the location string of the item on what shelf
        loc_rack (str): the location string of the item on what rack
        loc_box (str): the location string of the item on what box
        loc_row (str): the location string of the item on what row
        loc_col (str): the location string of the item on what column
        loc_depth (str): the location string of the item on what depth
        count (int): the current number of items in stock
        threshold (int): the minimum threshold before ordering more
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    cursor.execute(
        """SELECT count FROM items WHERE name = ? and is_metric = ? and size = ?""",
        (name, is_metric, size),
    )
    item = cursor.fetchone()
    if item is not None:
        new_count = item[0] + count
        cursor.execute(
            """UPDATE items set count = ? WHERE name = ? and is_metric = ? and size = ?""",
            (new_count, name, is_metric, size),
        )
    else:

        cursor.execute(
            """
                       INSERT INTO items
                       ( name, size, is_metric, loc_shelf, 
                       loc_rack, loc_box, loc_row, loc_col, loc_depth, count, threshold)
                       VALUES
                        (?,?,?,?,?,?,?,?,?,?,?)
                       """,
            (
                name,
                size,
                is_metric,
                loc_shelf,
                loc_rack,
                loc_box,
                loc_row,
                loc_col,
                loc_depth,
                count,
                threshold,
            ),
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

    Returns:
        None
    """
    cursor.execute(
        """
                    DELETE FROM items WHERE id = ?
                   """,
        (item_id,),
    )
    connection.commit()


def update_item(
    name: str,
    size: str,
    is_metric: bool,
    loc_shelf: str,
    loc_rack: str,
    loc_box: str,
    loc_row: str,
    loc_col: str,
    loc_depth: str,
    threshold: int,
    new_name: str,
    new_size: str,
    new_is_metric: bool,
    new_count: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    updates an item in the database

    Args:
        name (str): name of the item
        size (str): size of the item
        is_metric (int): whether the item is metric (1) or not (0)
        loc_shelf (str): the location string of the item on what shelf
        loc_rack (str): the location string of the item on what rack
        loc_box (str): the location string of the item on what box
        loc_row (str): the location string of the item on what row
        loc_col (str): the location string of the item on what column
        loc_depth (str): the location string of the item on what depth
        threshold (int): the minimum threshold before ordering more
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    item_id = find_by_name(name, is_metric, size, cursor)
    cursor.execute(
        """
                   UPDATE items SET name = ?, size = ?, is_metric = ?, loc_shelf = ?, 
                   loc_rack = ?, loc_box = ?, loc_row = ?, loc_col = ?, loc_depth = ?, count = ?, threshold = ? WHERE id = ?
                   """,
        (
            new_name,
            new_size,
            new_is_metric,
            loc_shelf,
            loc_rack,
            loc_box,
            loc_row,
            loc_col,
            loc_depth,
            new_count,
            threshold,
            item_id,
        ),
    )
    connection.commit()


def backup_data(cursor: sqlite3.Cursor) -> None:
    """
    Creates a backup of the database

    Args:
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries

    Returns:
        None
    """
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    # Assuming column names are available in cursor.description
    column_names = [description[0] for description in cursor.description]

    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Open the CSV file for writing
    with open(f"../data/data{date}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        print(f"Created backup file: data{date}.csv")

        # Write the header (column names)
        writer.writeheader()

        # Write the rows (data)
        for item in items:
            row = dict(zip(column_names, item))
            writer.writerow(row)

    print("Backup complete")


def get_backup_files() -> list[str]:
    """
    Returns a list of backup files

    Args:
        None

    Returns:
        list[str]: list of backup files
    """
    return glob.glob("../data/*.csv")


if __name__ == "__main__":
    connection = sqlite3.connect("../data/data.db")
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM items
        """
    )
    print(cursor.fetchall())
