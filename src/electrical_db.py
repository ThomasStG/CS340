"""
This module contains functions for interacting with the electrical database

Functions:
    ensure_tables()
    add_active_item_el()
    add_passive_item_el()
    search_similar_passive_items_el()
    search_active_el()
    search_passive_el()
    decrement_passive_item_el()
    decrement_active_item_el()
    increment_passive_item_el()
    increment_active_item_el()
    remove_active_item_el()
    remove_passive_item_el()
"""

import csv
import datetime
import glob
import json
import math
import sqlite3

from fuzzywuzzy import fuzz, process
from typing_extensions import Optional


def ensure_tables():
    """
    Ensures the user table exists in the database

    Args:
        None

    Returns:
        None
    """
    with sqlite3.connect("../data/data.db") as connection:
        cursor = connection.cursor()
        # cursor.execute(
        #     """
        #     DROP TABLE IF EXISTS electrical_active_items
        #     """
        # )
        # cursor.execute(
        #     """
        #     DROP TABLE IF EXISTS electrical_passive_items
        #     """
        # )
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS electrical_active_items (
                    id INTEGER PRIMARY KEY,
                    part_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    link TEXT NOT NULL,
                    location TEXT NOT NULL DEFAULT 'EL',
                    rack INTEGER NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    slot TEXT NOT NULL,
                    is_contacted INTEGER NOT NULL DEFAULT 0,
                    is_assembly INTEGER NOT NULL DEFAULT 0,
                    type TEXT DEFAULT ''
                )
                """
        )
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS electrical_passive_items (
                    id INTEGER PRIMARY KEY,
                    subtype TEXT NOT NULL,
                    value REAL NOT NULL,
                    mounting_method TEXT NOT NULL,
                    tolerance REAL,
                    part_number TEXT,
                    location TEXT NOT NULL DEFAULT 'EL',
                    rack INTEGER NOT NULL,
                    slot TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    link TEXT NOT NULL,
                    is_contacted INTEGER NOT NULL DEFAULT 0,
                    max_p REAL NOT NULL DEFAULT 0,
                    max_v REAL NOT NULL DEFAULT 0,
                    max_i REAL NOT NULL DEFAULT 0,
                    i_hold REAL,
                    polarity INTEGER,
                    seller TEXT,
                    dielectric_material TEXT
                )
                """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                tooltip TEXT,
                location TEXT NOT NULL DEFAULT 'EL' UNIQUE
            )
            """
        )
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS multipliers (
                    id INTEGER PRIMARY KEY,
                    type TEXT NOT NULL,
                    multiplier TEXT NOT NULL UNIQUE
                )
            """
        )
        calculate_multiplier(cursor, connection)
        connection.commit()


def add_active_item_el(
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
    name: str,
    part_id: str,
    location: str,
    rack: int,
    slot: str,
    count: int,
    link: str,
    description: str,
    item_type: str,
    is_assembly: bool = False,
):
    """
    Adds an item to the database

    Args:
        name (str): name of the item
        part_id (str): part number of the item
        rack (int): rack number of the item
        slot (str): slot number of the item
        count (int): count of the item
        link (str): link to the item
        description (str): description of the item
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    try:
        if location == "":
            location = "EL"
        cursor.execute(
            """
            INSERT INTO electrical_active_items (
                name,
                part_id,
                location,
                rack,
                slot,
                count,
                description,
                link,
                type,
                is_assembly
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                part_id,
                location,
                rack,
                slot,
                count,
                description,
                link,
                item_type,
                is_assembly,
            ),
        )
        print("Item added to database")
        connection.commit()
    except sqlite3.IntegrityError:
        print("Item already exists in database")
        connection.commit()


def add_passive_item_el(
    part_number: str,
    item_type: str,
    link: str,
    value: float,
    location: str,
    rack: int,
    slot: str,
    count: int,
    max_p: float,
    max_v: float,
    max_i: float,
    i_hold: float,
    tolerance: float,
    polarity: bool,
    seller: str,
    dielectric_material: str,
    mounting_method: str,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
):
    """
    Adds an item to the database

    Args:
        part_number (str): part number of the item
        item_type (str): type of the item
        link (str): link to the item
        value (float): value of the item
        rack (int): rack number of the item
        slot (str): slot number of the item
        count (int): count of the item
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    if not location:
        location = "EL"
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT * FROM electrical_passive_items
    WHERE value = ? AND subtype = ? AND tolerance = ? AND mounting_method = ? AND location = ? AND rack = ? AND slot = ?
    """,
        (value, item_type, tolerance, mounting_method, location, rack, slot),
    )
    old_item = cursor.fetchone()
    # TODO: Check if location is important to part_number changing

    if old_item and old_item["part_number"] == part_number:
        print("updating")
        update_passive_item_el(
            old_item["id"],
            part_number,
            item_type,
            link,
            value,
            location,
            rack,
            slot,
            count + old_item["count"],
            max_p,
            max_v,
            max_i,
            i_hold,
            tolerance,
            polarity,
            seller,
            dielectric_material,
            mounting_method,
            cursor,
            connection,
        )
        return
    cursor.execute(
        """
        INSERT INTO electrical_passive_items (
            part_number,
            subtype,
            link,
            value,
            location,
            rack,
            slot,
            count,
            max_p,
            max_v,
            max_i,
            i_hold,
            tolerance,
            polarity,
            seller,
            dielectric_material,
            mounting_method) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            part_number,
            item_type,
            link,
            value,
            location,
            rack,
            slot,
            count,
            max_p,
            max_v,
            max_i,
            i_hold,
            tolerance,
            polarity,
            seller,
            dielectric_material,
            mounting_method,
        ),
    )
    connection.commit()


def remove_active_item_el(
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
    item_id: Optional[int] = None,
    name: Optional[str] = None,
) -> None:
    """
    deletes an item from the database

    Args:
        item_id (int): item id to delete
        name (str): name of the item
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    cursor.execute(
        """
                    DELETE FROM electrical_active_items 
                    WHERE id = ? OR name = ?
                   """,
        (item_id, name),
    )
    connection.commit()


def remove_passive_item_el(
    item_type: str, item_id: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection
) -> None:
    """
    deletes an item from the database

    Args:
        item_id (int): item id to delete
        name (str): name of the item
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """

    # TODO: check if part number is unique.
    cursor.execute(
        """
                    DELETE FROM electrical_passive_items 
                    WHERE subtype = ? AND id = ?
                   """,
        (item_type, item_id),
    )
    connection.commit()


def update_passive_item_el(
    item_id: int,
    part_number: str,
    item_type: str,
    link: str,
    value: float,
    location: str,
    rack: int,
    slot: str,
    count: int,
    max_p: float,
    max_v: float,
    max_i: float,
    i_hold: float,
    tolerance: float,
    polarity: bool,
    seller: str,
    dielectric_material: str,
    mounting_method: str,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
):
    print(
        item_id,
        part_number,
        item_type,
        link,
        value,
        location,
        rack,
        slot,
        count,
        max_p,
        max_v,
        max_i,
        i_hold,
        tolerance,
        polarity,
        seller,
        dielectric_material,
        mounting_method,
    )
    cursor.execute(
        """
                    UPDATE electrical_passive_items 
                    SET part_number = ?, 
                        subtype = ?, 
                        link = ?, 
                        value = ?, 
                        location = ?, 
                        rack = ?, 
                        slot = ?, 
                        count = ?, 
                        max_p = ?, 
                        max_v = ?, 
                        max_i = ?, 
                        i_hold = ?, 
                        tolerance = ?, 
                        polarity = ?, 
                        seller = ?, 
                        dielectric_material = ?, 
                        mounting_method = ? 
                    WHERE id = ?
                   """,
        (
            part_number,
            item_type,
            link,
            value,
            location,
            rack,
            slot,
            count,
            max_p,
            max_v,
            max_i,
            i_hold,
            tolerance,
            polarity,
            seller,
            dielectric_material,
            mounting_method,
            item_id,
        ),
    )
    connection.commit()


def update_active_item_el(
    item_id: str,
    name: str,
    new_item_id: str,
    new_name: str,
    location: str,
    rack: int,
    slot: str,
    count: int,
    link: str,
    description: str,
    is_assembly: bool,
    subtype: str,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
):
    cursor.execute(
        """
                    UPDATE electrical_active_items 
                    SET part_id = ?,
                        name = ?, 
                        location = ?, 
                        rack = ?, 
                        slot = ?, 
                        count = ?, 
                        link = ?, 
                        description = ?,
                        is_assembly = ?,
                        type = ?
                    WHERE part_id = ? OR name = ?
                   """,
        (
            new_item_id,
            new_name,
            location,
            rack,
            slot,
            count,
            link,
            description,
            is_assembly,
            subtype,
            item_id,
            name,
        ),
    )
    connection.commit()


def increment_active_item_el(
    num_to_add: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
    item_id: Optional[int] = None,
    name: Optional[str] = None,
) -> None:
    """
    increments the count of an item in the active items table

    Args:
        item_id (int): id of the item
        name (str): name of the item
        num_to_add (int): number of items to add
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    cursor.execute(
        """
                    UPDATE electrical_active_items 
                    SET count = count + ? 
                    WHERE id = ? OR name = ?
                   """,
        (num_to_add, item_id, name),
    )
    connection.commit()


def increment_passive_item_el(
    item_id: int,
    num_to_add: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:
    """
    increments the count of an item in the passive items table

    Args:
        item_id (int): id of the item
        num_to_add (int): number of items to add
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries
        connection (sqlite3.Connection): SQLite connection object to commit changes

    Returns:
        None
    """
    cursor.execute(
        """
                    UPDATE electrical_passive_items 
                    SET count = count + ? 
                    WHERE id = ?
                   """,
        (num_to_add, item_id),
    )
    connection.commit()


def decrement_active_item_el(
    num_to_remove: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
    item_id: Optional[int] = None,
    name: Optional[str] = None,
) -> None:
    """
    Decrements the count of an item in the electrical_active_items table and checks threshold.

    Args:
        item_id (int): ID of the item.
        name (str): Name of the item.
        num_to_remove (int): Number of items to remove.
        cursor (sqlite3.Cursor): SQLite cursor object.
        connection (sqlite3.Connection): SQLite connection object.
    """
    if item_id is None and name is None:
        raise ValueError("Either item_id or name must be provided.")

    if item_id:
        cursor.execute(
            """
            SELECT item_id, count, is_contacted, threshold
            FROM electrical_active_items
            WHERE item_id = ?
        """,
            (item_id,),
        )
    else:
        cursor.execute(
            """
            SELECT item_id, count, is_contacted, threshold
            FROM electrical_active_items
            WHERE name = ?
        """,
            (name,),
        )

    row = cursor.fetchone()

    if row is None:
        raise ValueError("Item not found. No update performed.")

    item_id, count, is_contacted, threshold = row
    count -= num_to_remove

    contact_val = is_contacted

    # Check threshold and contact status
    if not is_contacted and count <= threshold:
        # TODO: Send Email
        contact_val = 1

    # Update and fetch in a single transaction
    cursor.execute(
        """
        UPDATE electrical_active_items
        SET count = count - ? is_contacted = ?
        WHERE id = ?
    """,
        (num_to_remove, contact_val, item_id),
    )

    connection.commit()


def decrement_passive_item_el(
    item_id: int,
    num_to_remove: int,
    cursor: sqlite3.Cursor,
    connection: sqlite3.Connection,
) -> None:

    # TODO: add  email/threshold check
    cursor.execute(
        """
                    UPDATE electrical_passive_items 
                    SET count = count - ? 
                    WHERE id = ?
                   """,
        (num_to_remove, item_id),
    )
    connection.commit()


def search_passive_el(
    cursor: sqlite3.Cursor,
    item_type: Optional[str] = None,
    value: Optional[int] = None,
    mounting_method: Optional[str] = None,
    tolerance: Optional[float] = None,
) -> list:
    """
    Search for passive items in the database.

    Args:
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries.
        item_type (Optional[str], optional): Type of the item. Defaults to None.
        value (Optional[int], optional): Value of the item. Defaults to None.
        mounting_method (Optional[str], optional): Mounting method of the item. Defaults to None.
        tolerance (Optional[float], optional): Tolerance of the item. Defaults to None.

    Returns:
        list: List of passive items that match the search criteria.
    """
    query = "SELECT * FROM electrical_passive_items WHERE location = 'EL'"
    conditions = []
    params = []

    if item_type:
        conditions.append("subtype = ?")
        params.append(item_type)
    if value:
        conditions.append("value = ?")
        params.append(value)
    if mounting_method:
        conditions.append("mounting_method = ?")
        params.append(mounting_method)
    if tolerance:
        conditions.append("tolerance = ?")
        params.append(tolerance)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    print(query)
    print(params)

    cursor.execute(query, params)

    output = [{**dict(row), "type": "passive"} for row in cursor.fetchall()]
    return output


def search_active_el(
    cursor: sqlite3.Cursor,
    item_id: Optional[int] = None,
    name: Optional[str] = None,
) -> list:
    """
    Search for active items in the database.

    Args:
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries.
        item_id (Optional[int], optional): ID of the item. Defaults to None.
        name (Optional[str], optional): Name of the item. Defaults to None.

    Returns:
        list: List of active items that match the search criteria.
    """
    query = "SELECT * FROM electrical_active_items WHERE location = 'EL'"
    conditions = []
    params = []

    if item_id:
        conditions.append("id = ?")
        params.append(item_id)
    if name:
        conditions.append("name = ?")
        params.append(name)

    if conditions:
        query += " AND ".join(conditions)

    cursor.execute(query, params)
    output = [{**dict(row), "type": "active"} for row in cursor.fetchall()]
    return output


def search_similar_passive_items_el(
    cursor: sqlite3.Cursor,
    value: float,
    search_percent: float = 0.50,
    item_type: Optional[str] = None,
    tolerance: Optional[float] = None,
    mounting_method: Optional[str] = None,
) -> list[dict]:
    """
    Search for similar passive items in the database.

    Args:
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries.
        value (int): The value of the passive item.
        search_percent (float): The percentage to search around the value should be passed as 20 for 20%.
        item_type (Optional[str], optional): The type of the passive item. Defaults to None.
        tolerance (Optional[float], optional): The tolerance of the passive item. Defaults to None.
        mounting_method (Optional[str], optional): The mounting method of the passive item. Defaults to None.

    Returns:
        list: List of similar passive items.
    """
    query = "SELECT * FROM electrical_passive_items WHERE location = 'EL' "
    conditions = []
    params = []
    search_delta = value * search_percent
    conditions.append("AND value BETWEEN ? AND ?")
    params.append(value - search_delta)
    params.append(value + search_delta)

    if item_type:
        conditions.append("subtype = ?")
        params.append(item_type)
    if mounting_method:
        conditions.append("mounting_method = ?")
        params.append(mounting_method)
    if tolerance:
        conditions.append("tolerance >= ?")
        params.append(tolerance)

    if conditions:
        query += " AND ".join(conditions) + " ORDER BY value DESC"

    print(query)
    print(params)

    cursor.execute(query, params)
    items = cursor.fetchall()
    for item in items:
        print("item: ", item)

    output = [{**dict(row), "type": "passive"} for row in items]
    return output


def search_similar_active_items_el(
    cursor: sqlite3.Cursor,
    name: Optional[str] = "",
    part_id: Optional[str] = "",
    is_assembly: bool = False,
    top_n: int = 10,
) -> list:
    """
    Search for similar active items in the database based on `name`, `part_id`, or both.

    Args:
        cursor (sqlite3.Cursor): SQLite cursor object to execute queries.
        name (Optional[str]): Name of the item to search for (fuzzy matching).
        part_id (Optional[str]): Part ID to search for (fuzzy matching).
        top_n (int): Number of top matches to return.

    Returns:
        list: List of dictionaries containing matched active items.
    """

    # Normalize inputs by stripping and converting to lowercase
    if name:
        name = name.strip().lower()
    if part_id:
        part_id = part_id.strip().lower()

    # Initial query to get all data from the database
    cursor.execute(
        "SELECT * FROM electrical_active_items WHERE is_assembly = ? AND location = 'EL'",
        (is_assembly,),
    )
    data = cursor.fetchall()

    if not data:
        return []

    # Convert rows to dictionaries
    row_dict = {row["part_id"]: dict(row) for row in data}

    # Create a dictionary {id: "name"} for fuzzy matching
    choices = {row["part_id"]: f"{row['name']}" for row in data}

    # Build the search query based on user input
    search_query = []

    # Add conditions for `name` or `part_id` if provided
    if name:
        search_query.append(name)
    if part_id:
        search_query.append(part_id)

    # Combine all search terms into one string
    query = " ".join(search_query)

    # Perform fuzzy matching with the combined query
    best_matches = process.extract(
        query, choices, scorer=fuzz.partial_ratio, limit=top_n
    )

    # Extract full rows as dictionaries using their IDs
    results = [{**row_dict[match[2]], "type": "active"} for match in best_matches]

    return results  # Return structured output


def search_below_threshold_el(
    cursor: sqlite3.Cursor,
    tables: list[str] = [],
    types: list[str] = [],
    threshold: int = 50,
) -> list[dict]:
    """ """
    table_dict = {
        "passive": "electrical_passive_items",
        "active": "electrical_active_items",
        "assembly": "electrical_active_items",
    }
    output = []

    for table in tables:
        query = f"SELECT * FROM {table_dict[table]} WHERE count <= ?"
        params: list = [threshold]

        if table == "passive":
            if types:
                placeholders = ",".join("?" for _ in types)
                query += f" AND type IN ({placeholders})"
                params.extend(types)

        query += " AND location = 'EL'"

        cursor.execute(query, params)
        output.extend({**dict(row), "type": table} for row in cursor.fetchall())
    return output


def update_tooltip(
    cursor: sqlite3.Cursor, connection: sqlite3.Connection, tooltip: str
) -> None:
    """
    Update the tooltip value in the database.

    Args:
        tooltip (str): The new tooltip value to be stored in the database.

    Returns:
        None
    """
    cursor.execute(
        """
            UPDATE settings SET tooltip = ? WHERE location = 'EL'
        """,
        (tooltip,),
    )
    connection.commit()


def get_tooltip(cursor: sqlite3.Cursor) -> str:
    """
    Get the tooltip value from the database.

    Returns:
        str: The tooltip value stored in the database.
    """
    cursor.execute(
        """
            SELECT tooltip FROM settings WHERE location = 'EL'
        """
    )
    return cursor.fetchone()[0]


def calculate_multiplier(cursor: sqlite3.Cursor, connection: sqlite3.Connection):
    types = [
        "Resistor",
        "capacitor",
        "polyfuse",
    ]

    type_dict = {
        "Resistor": "Ohm",
        "capacitor": "Farad",
        "polyfuse": "Ohm",
        "oscillator": "Hertz",
    }

    multiplier_dict = {
        -12: "p",  # pico
        -9: "n",  # nano
        -6: "u",  # micro
        -3: "m",  # milli
        -2: "c",  # centi
        -1: "d",  # deci
        0: "",  # no prefix
        3: "k",  # kilo
        6: "M",  # mega
        9: "G",  # giga
        12: "T",  # tera
    }

    cursor.execute(
        """
        DELETE FROM multipliers WHERE 1
        """
    )
    connection.commit()

    for item_type in types:
        cursor.execute(
            """
            SELECT DISTINCT value FROM electrical_passive_items 
            WHERE LOWER(subtype) = LOWER(?) AND value != 0 ORDER BY value DESC
            """,
            (item_type,),
        )
        rows = [row[0] for row in cursor.fetchall()]

        if len(rows) == 0:
            continue

        max_value = rows[0]
        min_value = rows[-1]

        min_power = math.floor(math.log10(min_value))
        min_rounded_power = int(3 * round(min_power / 3))

        max_power = math.floor(math.log10(max_value))
        rounded_power = int(3 * round(max_power / 3))

        prefixes = [""]
        for i in range(min_rounded_power, rounded_power + 1):
            prefix = multiplier_dict.get(i)
            if prefix:
                prefixes.append(prefix)

        if len(prefixes) == 0:
            continue

        mult = json.dumps(prefixes)
        cursor.execute(
            """
            INSERT INTO multipliers (type, multiplier) VALUES (?, ?)
            """,
            (
                item_type,
                mult,
            ),
        )

    connection.commit()


def get_multiplier(cursor: sqlite3.Cursor):
    type_dict = {
        "Resistor": "Ohm",
        "Capacitor": "Farad",
        "Polyfuse": "Ohm",
    }
    value_dict = {
        "p": 10**-12,
        "n": 10**-9,
        "u": 10**-6,
        "m": 10**-3,
        "c": 10**-2,
        "d": 10**-1,
        "": 1,
        "k": 10**3,
        "M": 10**6,
        "G": 10**9,
        "T": 10**12,
    }
    results = []
    for item_type in type_dict.items():
        cursor.execute(
            """
            SELECT multiplier FROM multipliers WHERE type = ?
            """,
            (item_type[0],),
        )
        rows = cursor.fetchall()
        mults = []
        values = []
        for row in rows:
            for element in json.loads(row[0]):
                mults.append(element + item_type[1])
        for multiplier_type in mults:
            prefix = multiplier_type[0]
            value = value_dict.get(prefix, 1)
            values.append(value)
        results.append({"type": item_type[0], "multiplier": mults, "values": values})
    print(results)

    return results


def get_backup_files_el() -> list[str]:
    """
    Returns a list of backup files

    Args:
        None

    Returns:
        list[str]: list of backup files
    """
    files = glob.glob("../data/electrical_lab/*.csv")
    print(files)
    return files


def backup_data_el(cursor: sqlite3.Cursor) -> None:
    """
    Creates a backup of the electrical database by combining passive and active items
    into one CSV file with a 'type' column added to distinguish between them.
    """
    # Fetch passive items
    cursor.execute("SELECT * FROM electrical_passive_items")
    passive_items_raw = cursor.fetchall()
    passive_columns = [desc[0] for desc in cursor.description]
    passive_columns.append("type")

    # Add type tag to each passive item
    passive_items = [item + ("passive",) for item in passive_items_raw]

    # Fetch active items
    cursor.execute("SELECT * FROM electrical_active_items")
    active_items_raw = cursor.fetchall()
    active_columns = [desc[0] for desc in cursor.description]
    active_columns.append("type")

    # Add type tag to each active item
    active_items = [item + ("active",) for item in active_items_raw]

    # Combine columns and remove duplicates
    column_names = list(set(passive_columns + active_columns))

    # Merge rows
    rows = []
    for item in passive_items:
        row = dict(zip(passive_columns, item))
        full_row = {col: row.get(col, "") for col in column_names}
        rows.append(full_row)

    for item in active_items:
        row = dict(zip(active_columns, item))
        full_row = {col: row.get(col, "") for col in column_names}
        rows.append(full_row)

    # Write to CSV
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(
        f"../data/electrical_lab/data-{date}.csv", "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        print(f"Created backup file: data-{date}.csv")
        writer.writeheader()
        writer.writerows(rows)

    print("Backup complete")
