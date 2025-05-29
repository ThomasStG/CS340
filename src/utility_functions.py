"""
This module provides utility functions for the API

It contains functions to:
    - Initialize a connection to the database
    - Handle exceptions thrown by the API
    - Generate a JWT token for a user
    - import data from a CSV file in two ways
    - parse a location string into a list
"""

import csv
import datetime
import io
import json
import logging
import math
import os
import sqlite3
from pathlib import Path
from typing import Tuple

import jwt
from dotenv import load_dotenv
from flask import Response, g, jsonify

from electrical_db import add_active_item_el, add_passive_item_el
from idea_db import add_item


def get_db() -> sqlite3.Connection:
    """
    Initializes a connection to the database using a global varialbe

    Returns:
        g.db (sqlite3.Connection): the connection.
    """
    if "db" not in g:
        g.db = sqlite3.connect("../data/data.db")
        g.db.row_factory = sqlite3.Row  # Allows dictionary-like row access
    return g.db


def handle_exceptions(exception: Exception) -> Tuple[Response, int]:
    """
    Handles exceptions thrown by the API

    Args:
        exception (Exception): the exception thrown

    Returns:
        jsonify: a message and status code
    """
    if isinstance(exception, KeyError):
        return (
            jsonify(
                {"status": "error", "message": f"Invalid request: {str(exception)}"}
            ),
            400,
        )
    elif isinstance(exception, ValueError):
        return (
            jsonify({"status": "error", "message": f"Invalid value: {str(exception)}"}),
            422,
        )
    elif isinstance(exception, sqlite3.IntegrityError):
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    elif isinstance(exception, sqlite3.OperationalError):
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    else:
        return (
            jsonify(
                {"status": "error", "message": f"Unexpected error: {str(exception)}"}
            ),
            500,
        )


def generate_token(username: str, level: int) -> str:
    """
    Generates a JWT token for a user

    Args:
        username (str): the username of the user
        level (int): the access level of the user

    Returns:
        str: the JWT token
    """
    load_dotenv("data/.env")
    secret_key = os.environ.get("Login_Token_Secret_Key")
    payload = {
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=30),
        "username": username,
        "access": level,
    }
    try:
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        return token
    except Exception as e:
        raise


def delete_backup(file_path: str) -> None:
    """
    Deletes a backup file

    Args:
        file_path (str): the path to the backup file

    Returns:
        None
    """
    os.remove(file_path)


def import_csv(uri: str) -> None:
    """
    Imports a CSV file into the database

    Args:
        uri (str): the path to the CSV file

    Returns:
        None
    """
    try:
        # Ensure the file exists
        file_path = Path(uri)
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {uri}")

        # Connect to the database
        with sqlite3.connect("../data/data.db") as con:
            cur = con.cursor()

            # Delete all previous data from 'items' table
            cur.execute("DELETE FROM items")

            # Open and read the file
            with open(uri, "r", newline="") as file:
                reader = csv.reader(file)
                headers = next(reader)  # Skip header

                for row in reader:
                    # Skip empty or malformed rows
                    if len(row) < 13:
                        continue

                    try:
                        if len(row) > 13:
                            add_item(
                                row[0],  # name
                                row[1],  # size
                                row[2] == "1",  # is_metric as bool
                                row[3],  # loc_shelf
                                row[4],  # loc_rack
                                row[5],  # loc_box
                                row[6],  # loc_row
                                row[7],  # loc_col
                                row[8],  # loc_depth
                                int(row[9]),  # count
                                int(row[10]),  # threshold
                                cur,
                                con,
                            )
                        else:
                            add_item(
                                row[1],  # name
                                row[2],  # size
                                row[3] == "1",  # is_metric as bool
                                row[4],  # loc_shelf
                                row[5],  # loc_rack
                                row[6],  # loc_box
                                row[7],  # loc_row
                                row[8],  # loc_col
                                row[9],  # loc_depth
                                int(row[10]),  # count
                                int(row[11]),  # threshold
                                cur,
                                con,
                            )
                    except Exception as row_err:
                        raise row_err

            con.commit()

    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except sqlite3.DatabaseError as db_error:
        print(f"Database error: {db_error}")
    except Exception as e:
        print(f"Error importing CSV: {e}")


def add_from_csv(file_stream: bytes) -> None:
    """
    Adds values from a CSV file to the database

    Args:
        uri (str): the filepath to the CSV file

    Returns:
        None
    """
    try:
        con = sqlite3.connect("../data/data.db")
        cur = con.cursor()
        reader = csv.DictReader(io.StringIO(file_stream.decode("utf-8")))
        data = [row for row in reader]

        for row in data:
            try:
                if len(row) > 13:
                    add_item(
                        row[0],  # name
                        row[1],  # size
                        row[2] == "1",  # is_metric as bool
                        row[3],  # loc_shelf
                        row[4],  # loc_rack
                        row[5],  # loc_box
                        row[6],  # loc_row
                        row[7],  # loc_col
                        row[8],  # loc_depth
                        int(row[9]),  # count
                        int(row[10]),  # threshold
                        cur,
                        con,
                    )
                else:
                    add_item(
                        row[1],  # name
                        row[2],  # size
                        row[3] == "1",  # is_metric as bool
                        row[4],  # loc_shelf
                        row[5],  # loc_rack
                        row[6],  # loc_box
                        row[7],  # loc_row
                        row[8],  # loc_col
                        row[9],  # loc_depth
                        int(row[10]),  # count
                        int(row[11]),  # threshold
                        cur,
                        con,
                    )
            except Exception as row_err:
                print(f"Error processing row {row}: {row_err}")

        con.commit()  # Commit changes
    except Exception as e:
        print(f"Error importing CSV: {e}")


def parse_location_to_list(item: dict) -> list:
    """
    Parses a json string into a location

    Args:
        item (dict): Item data
    Returns:
        list: representing the json location
    """
    return [
        str(item.get("loc_shelf", "")).strip(),
        str(item.get("loc_rack", "")).strip(),
        str(item.get("loc_box", "")).strip(),
        str(item.get("loc_row", "")).strip(),
        str(item.get("loc_col", "")).strip(),
        str(item.get("loc_depth", "")).strip(),
    ]


def safe_int(value, default=0) -> int:
    """
    Safely converts a string to an integer

    Args:
        value (str): the value to convert
        default (int, optional): the default value to return if the conversion fails. Defaults to 0.

    Returns:
        int: the converted value
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0) -> float:
    """
    Safely converts a string to a float

    Args:
        value (str): the value to convert
        default (float, optional): the default value to return if the conversion fails. Defaults to 0.0.

    Returns:
        float: the converted value
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def refresh_from_csv_el(uri: str) -> None:
    """
    Refreshes the database from a CSV file

    Args:
        uri (str): the filepath to the CSV file

    Returns:
        None
    """
    with sqlite3.connect("../data/data.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM electrical_passive_items")
        cur.execute("DELETE FROM electrical_active_items")
        con.commit()
    import_csv_el(uri)


def import_csv_el(uri: str) -> None:
    """
    Imports a CSV file into the database

    Args:
        uri (str): the filepath to the CSV file

    Returns:
        None
    """
    with sqlite3.connect("../data/data.db") as con:
        cur = con.cursor()
        with open(uri, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]

            for row in data:
                try:
                    match (row["Type"]):
                        case "passive":
                            add_passive_item_el(
                                value=float(row["Ref Value (Ohms)"]),
                                max_p=float(row["Max. P (W)"]),
                                max_v=float(row["Max. V (V)"]),
                                max_i=float(row["Max. I (A)"]),
                                i_hold=float(row["I Hold (A)"]),
                                tolerance=float(row["Tolerance (+/-%)"]),
                                mounting_method=row["Mounting Method"],
                                location=row["Location"],
                                rack=int(row["Rack"]),
                                slot=row["Slot"],
                                part_number=row["Part #"],
                                dielectric_material=row["Dielectric Material"],
                                item_type=row["Subtype"],
                                link=row["Link"],
                                count=int(row["Count"]),
                                polarity=bool(row["Polarity"]),
                                seller=row["Seller"],
                                cursor=cur,
                                connection=con,
                            )
                        case "active":
                            add_active_item_el(
                                cursor=cur,
                                connection=con,
                                name=row["Name*"],
                                description=row["Description"],
                                part_id=row["Ref. ID*"],
                                location=row["Location"],
                                rack=int(row["Rack"]),
                                slot=row["Slot"],
                                count=int(row["Count"]),
                                link=row["Link"],
                                item_type=row["Subtype"],
                                is_assembly=row["Is Assembly"] == "1",
                            )
                    con.commit()
                except sqlite3.IntegrityError as e:
                    print(f"Integrity error processing row {row}: {e}")
                except sqlite3.OperationalError as e:
                    print(f"Operational error processing row {row}: {e}")
                except Exception as e:
                    print(f"General error: {e} | Row: {row}")
                    import traceback

                    traceback.print_exc()
