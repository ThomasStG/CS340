"""
This module provides an API for an inventory management system.

Functions:
    get_db: Initializes a connection to the database using a global variable.
    handle_exceptions: Handles exceptions raised by the API.
    generate_token: Generates a login token for a user.
    teardown_db: Cleans up the connections and global variable on quit.
    import_csv: Deletes all items from the database and repopulates with values from a CSV file.
    add_from_csv: Adds items from a CSV file to the database.
    parse_location_to_string: Parses a JSON string into a location.
    parse_location_to_list: Parses a JSON string into a list.
    run_server: Ensures the database has the required table for items,
                then runs the development server.

Endpoints:
    /api/addItem: Adds a new item to the database.
    /api/find: Returns a specific item from the database.
    /api/findAll: Returns all items from the database.
    /api/increment: Increments an item's count by `num_added`.
    /api/decrement: Decrements an item's count by `num_removed`.
    /api/remove: Deletes an item from the database.
    /api/fuzzyfind: Returns a list of items that are similar to the search term.
    /api/updateitem: Updates an item in the database.

    /api/register: Registers a new user.
    /api/trylogin: Tries to log in a user.
    /api/isLoggedIn: Checks if a user is logged in.
    /api/updateUser: Updates a user's password or access level.
    /api/checkToken: Checks if a token is valid.
    /api/getUsers: Returns a list of users.
    /api/deleteUser: Deletes a user.

    /api/backupDatabase: Backs up the database.
    /api/restoreDatabase: Restores the database from a backup.
    /api/getFiles: Returns a list of files in the database.
    /api/uploadFile: Uploads a file to the database.
    /api/appendFile: Appends a file to the database.
    /api/downloadFile: Downloads a file from the database.
    /api/getBackupFiles: Returns a list of backup files.

    /api/get_log: Returns a list of log entries.
"""

import datetime
import csv
import hashlib
import json
import logging
import os
import sqlite3
from io import BytesIO
from logging.handlers import TimedRotatingFileHandler
from typing import Tuple
from pathlib import Path

import jwt
import pandas as pd
import resend
from dotenv import load_dotenv
from flask import Flask, Response, g, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from api import (
    add_item,
    backup_data,
    build_db,
    decrement_item,
    find_by_name,
    fzf,
    get_all,
    get_backup_files,
    get_item,
    increment_item,
    remove_item,
    update_item,
)
from auth import (
    change_password,
    check_token,
    create_account,
    get_salt,
    login,
    get_users,
    delete_user,
)

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:8080"],
    methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
log = logging.getLogger("werkzeug")
log.disabled = True  # Enable CORS for Angular frontend


def get_db() -> sqlite3.Connection:
    """
    Initializes a connection to the database using a global varialbe

    Returns:
        g.db (sqlite3.Connection): the connection.
    """
    if "db" not in g:
        g.db = sqlite3.connect("..data/data.db")
        g.db.row_factory = sqlite3.Row  # Allows dictionary-like row access
    return g.db


@app.teardown_appcontext
def teardown_db(_: Exception) -> None:
    """
    Cleans up the connections and global variable on quit.

    Args:
        exception (Exception): automatically called by Flask

    Returns:
        None
    """
    db = g.pop("db", None)

    # closes the connection if it exists
    if db is not None:
        db.close()


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
        print(e)
        raise


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
                        print(f"Skipping row (too short): {row}")
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
                        print(f"Error processing row {row}: {row_err}")

            con.commit()
            print("Data imported successfully.")

    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except sqlite3.DatabaseError as db_error:
        print(f"Database error: {db_error}")
        con.rollback()
    except Exception as e:
        print(f"Error importing CSV: {e}")
        con.rollback()


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
        print("Connected to database")
        reader = csv.DictReader(file_stream)
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

        print("Data imported successfully")

        con.commit()  # Commit changes
    except Exception as e:
        con.rollback()
        print(f"Error importing CSV: {e}")
    finally:
        con.close()


def parse_location_to_string(location: str) -> str:
    """
    Parses a json string into a location

    Args:
        location (str): a json string
    Returns:
        str: representing the json location
    """
    return json.dumps(location)


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


@app.route("/increment", methods=["GET"])
def increment() -> Tuple[Response, int]:
    """
    Handles incrementing an item count in the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       num (int): the number to increment by
       token (str): the cookie of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.args
        if not data or not all(
            key in data for key in ["name", "is_metric", "size", "num", "token"]
        ):
            raise KeyError("Missing required parameters")

        token = data["token"]
        username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
        )

        if not check_token(token, username, cursor):
            raise ValueError("Invalid token")

        logger = logging.getLogger("app")
        logger.info(
            f"User '{username}' incremented '{data['name']} {data['size']}' by {data['num']}"
        )

        # find item
        item_id = find_by_name(
            data["name"],
            data["is_metric"].strip().lower() == "true",
            data["size"],
            cursor,
        )
        if item_id is None:
            raise ValueError("Item not found")

        # increment item
        increment_item(
            item_id,
            int(data["num"]),
            cursor,
            connection,
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/decrement", methods=["GET"])
def decrement() -> Tuple[Response, int]:
    """
    Handles decrementing an item count in the database.
    Data is passed from frontend through a GET request
    Additionally sends an email when a threshold is reached

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       num (int): the number to decrement by
       token (str): the cookie of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.args
        if not data or not all(
            key in data for key in ["name", "is_metric", "size", "num", "token"]
        ):
            raise KeyError("Missing required parameters")

        # check token
        token = data["token"]
        username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
        )

        if not check_token(token, username, cursor):
            raise ValueError("Invalid token")

        logger = logging.getLogger("app")
        logger.info(
            f"User '{username}' decremented '{data['name']} {data['size']}' by {data['num']}"
        )

        # find item
        item_id = find_by_name(
            data["name"],
            data["is_metric"].strip().lower() == "true",
            data["size"],
            cursor,
        )
        if item_id is None:
            raise ValueError("Item not found")

        name = data["name"]
        size = data["size"]
        is_metric = data["is_metric"].strip().lower() == "true"
        # decrement item
        message_status = decrement_item(
            item_id,
            int(data["num"]),
            cursor,
            connection,
        )
        if message_status == 1:
            # send email
            try:
                load_dotenv("data/.env")
                print("Resend API Key:", os.getenv("Resend_API"))
                resend.api_key = os.getenv("Resend_API")
                _ = resend.Emails.send(
                    {
                        "from": "onboarding@resend.dev",
                        "to": "i91503647@gmail.com",
                        "subject": f"{name} {size} is running low!",
                        "html": f"""
                        <h2>Stock Reminder</h2>
                        <p>This is a reminder to stock up on <strong>{name} {size}</strong>.</p>
                        """,
                    }
                )
                print("Sending Email")
            except Exception as e:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"There was an error sending the email: {str(e)}",
                        }
                    ),
                    500,
                )

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/find", methods=["GET"])
def find_item() -> Tuple[Response, int]:
    """
    Handles finding an item the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.args
        if (
            not data
            or "name" not in data
            or "is_metric" not in data
            or "size" not in data
        ):
            raise KeyError("Missing required parameters")

        # convert metric_val to a bool
        metric_val = int(data["is_metric"].strip().lower() == "true")
        item_id = find_by_name(data["name"], metric_val, data["size"], cursor)
        if item_id is None:
            raise ValueError("Item not found")
        item = get_item(item_id, cursor)

        if (
            isinstance(item, dict)
            and "loc_shelf" in item
            and item.get("loc_shelf") is not None
        ):
            item["location"] = parse_location_to_list(item)
        item[0]["is_metric"] = data["is_metric"].strip().capitalize()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Item found successfully",
                    "data": item,
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


@app.route("/addItem", methods=["GET"])
def add() -> Tuple[Response, int]:
    """
    Handles adding a new item the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       num (int): the number of the item
       threshold (int): the threshold of the item
       loc_shelf (str): the location of the item on what shelf
       loc_rack (str): the location of the item on what rack
       loc_box (str): the location of the item on what box
       loc_row (str): the location of the item on what row
       loc_col (str): the location of the item on what column
       loc_depth (str): the location of the item on what depth
       token (str): the cookie of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    print("Adding item...")

    try:
        connection = get_db()
        cursor = connection.cursor()
        print("Connected to database")
        data = request.args
        print(dict(request.args))
        if not data or not all(
            key in data
            for key in [
                "name",
                "is_metric",
                "size",
                "loc_shelf",
                "loc_rack",
                "loc_box",
                "loc_row",
                "loc_col",
                "loc_depth",
                "num",
                "threshold",
                "token",
            ]
        ):
            raise KeyError("Missing required parameters")
        token = data["token"]
        username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
        )

        if not check_token(token, username, cursor):
            raise ValueError("Invalid token")

        logger = logging.getLogger("app")
        logger.info(
            f"User '{username}' added item with name: {data['name']}, size: {data['size']}, is_metric: {data['is_metric']}, num: {data['num']}, threshold: {data['threshold']}, loc_shelf: {data['loc_shelf']}, loc_rack: {data['loc_rack']}, loc_box: {data['loc_box']}, loc_row: {data['loc_row']}, loc_col: {data['loc_col']}, loc_depth: {data['loc_depth']}"
        )

        add_item(
            data["name"],
            data["size"],
            data["is_metric"].strip().lower() == "true",
            data["loc_shelf"],
            data["loc_rack"],
            data["loc_box"],
            data["loc_row"],
            data["loc_col"],
            data["loc_depth"],
            int(data["num"]),
            int(data["threshold"]),
            cursor,
            connection,
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/remove", methods=["GET"])
def remove() -> Tuple[Response, int]:
    """
    Handles removing an item from the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       token (str): the cookie of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.args
        if not data or not all(
            key in data for key in ["name", "is_metric", "size", "token"]
        ):
            raise KeyError("Missing required parameters")
        token = data["token"]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        username = decoded_token.get("username")
        level = decoded_token.get("level")

        if not check_token(token, username, cursor):
            raise ValueError("Invalid token")
        if level > 1:
            raise ValueError("User does not have permission to remove items")

        logger = logging.getLogger("app")
        logger.info(
            f"User '{username}' removed item with name: {data['name']}, size: {data['size']}, is_metric: {data['is_metric']}"
        )

        # find item
        item_id = find_by_name(
            data["name"],
            data["is_metric"].strip().lower() == "true",
            data["size"],
            cursor,
        )
        if item_id is None:
            raise ValueError("Item not found")

        # remove item
        remove_item(item_id, cursor, connection)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/fuzzyfind", methods=["GET"])
def fuzzy() -> Tuple[Response, int]:
    """
    Handles finding similar items in the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.args
        if not data or not all(key in data for key in ["name", "is_metric", "size"]):
            raise KeyError("Missing required parameters")

        metric_val = int(data["is_metric"].strip().lower() == "true")
        items = fzf(data["name"], metric_val, data["size"], cursor)

        # parse location and convert is_metric to string
        for item in items:
            if "loc_shelf" in item and item["loc_shelf"] is not None:
                item["location"] = parse_location_to_list(item)
            item["is_metric"] = str(metric_val)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Item found successfully",
                    "data": items,
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


@app.route("/findAll", methods=["GET"])
def list_all() -> Tuple[Response, int]:
    """
    Handles retrieving all items in the database.
    Data is passed from frontend through a GET request

    Args:
        None

    Returns:
        Tuple[Response, int]: a message with possible data and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()

        # gets all items and converts is_metric to string
        items = get_all(cursor)
        for item in items:
            item["is_metric"] = str(item["is_metric"] == 1)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "items found successfully",
                    "data": items,
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


@app.route("/updateitem", methods=["GET"])
def update() -> Tuple[Response, int]:
    """
    Handles updating an item in the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       new_name (str): the new name of the item
       new_size (str): the new size of the item
       new_is_metric (int): whether the item is metric (1) or not (0)
       loc_shelf (str): the location of the item on what shelf
       loc_rack (str): the location of the item on what rack
       loc_box (str): the location of the item on what box in the rack
       loc_row (str): the location of the item on what row in the box
       loc_col (str): the location of the item on what column in the row
       loc_depth (str): the location of the item on what depth in the box
       num (int): the number to increment by
       threshold (int): the threshold of the item
       id (int): the id of the item
       token (str): the cookie of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        print("Updating item...")
        data = request.args
        if not data or not all(
            key in data
            for key in [
                "name",
                "is_metric",
                "size",
                "new_name",
                "new_size",
                "new_is_metric",
                "loc_shelf",
                "loc_rack",
                "loc_box",
                "loc_row",
                "loc_col",
                "loc_depth",
                "count",
                "threshold",
                "id",
                "token",
            ]
        ):
            raise KeyError("Missing required parameters")

        logger = logging.getLogger("app")
        try:
            token = data["token"]
            username = jwt.decode(token, options={"verify_signature": False}).get(
                "username"
            )
            if not check_token(token, username, get_db().cursor()):
                raise KeyError("Invalid token")
            logger.info(
                f"User: '{username}' updated item: {data['size']} {data['name']}"
            )
        except Exception as e:
            logger.error("An invalidated user attempted to update an item")
            return jsonify({"status": "error", "output": "false"}), 401

        connection = get_db()
        cursor = connection.cursor()
        update_item(
            data["name"],
            data["size"],
            data["is_metric"].strip().lower() == "true",
            data["loc_shelf"],
            data["loc_rack"],
            data["loc_box"],
            data["loc_row"],
            data["loc_col"],
            data["loc_depth"],
            int(data["threshold"]),
            data["new_name"],
            data["new_size"],
            data["new_is_metric"].strip().lower() == "true",
            data["count"],
            cursor,
            connection,
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/trylogin", methods=["POST"])
def try_login() -> Tuple[Response, int]:
    """
    Attempts to log the user in

    Args:
        username (str): the username of the user
        password (str): the hashed password of the user

    Returns:
        Tuple[Response, int]: a message with possible auth token and status code
    """
    try:
        data = request.json
        if data is None or "username" not in data or "password" not in data:
            raise KeyError("Missing required parameters")

        username = data["username"]
        password = data["password"]
        connection = get_db()
        cursor = connection.cursor()
        stored_salt = get_salt(username, cursor)

        salt = bytes.fromhex(stored_salt)  # Convert hex string back to bytes

        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()

        #     # Update the hash object with the salt and password
        hash_object.update(salt + password.encode("utf-8"))

        #     # Get the hashed password as a hexadecimal string
        hashed_password = hash_object.hexdigest()
        token = login(username, hashed_password, cursor, connection)
        if token == "":
            raise Exception("Login failed")
        return jsonify({"status": "success", "token": token}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/isLoggedIn", methods=["POST"])
def is_logged_in() -> Tuple[Response, int]:
    """
    Checks if the user is logged in

    Args:
        token (str): the token of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.json
        if data is None or "token" not in data:
            raise KeyError("Missing required parameters")

        token = data["token"]
        username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
        )
        if check_token(token, username, cursor):
            return jsonify({"status": "success", "output": "true"}), 200
        return jsonify({"status": "error", "output": "false"}), 401
    except Exception as e:
        return handle_exceptions(e)


@app.route("/register", methods=["POST"])
def register() -> Tuple[Response, int]:
    """
    Registers a new user

    Args:
        username (str): the username of the user
        password (str): the hashed password of the user
        level (int): the level of the user
        token (str): the token of the current logged in user

    Returns:
        Tuple[Response, int]: a message with possible auth token and status code
    """
    try:
        data = request.json
        if not data or any(
            key not in data for key in ["username", "password", "level", "token"]
        ):
            raise KeyError("Missing required parameters")

        username = data["username"]
        password = data["password"]
        level = int(data["level"])
        token = data["token"]
        auth_level = jwt.decode(token, options={"verify_signature": False}).get("level")
        test_username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
        )
        if not check_token(auth_token, test_username, cursor):
            raise ValueError("Invalid token")
        if not auth_level == 0:
            raise ValueError("Unauthorized")
        connection = get_db()
        cursor = connection.cursor()
        salt = os.urandom(32)

        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()

        # Update the hash object with the salt and password
        hash_object.update(salt + password.encode("utf-8"))

        # Get the hashed password as a hexadecimal string
        hashed_password = hash_object.hexdigest()

        create_account(username, level, hashed_password, salt.hex(), cursor, connection)
        token = generate_token(username, level)
        return jsonify({"status": "success", "token": token}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/updateUser", methods=["POST"])
def change_pass() -> Tuple[Response, int]:
    """
    Handles changing a user's password

    Args:
        username (str): the username of the user
        level str: the cookie of the user
        new_password (str): the new password of the user
        token (str): the token of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.json
        if not data or not all(
            k in data for k in ("username", "password", "level", "token")
        ):
            raise KeyError("Missing required parameters")

        username = data["username"]
        new_password = data["password"]
        level = data["level"]
        token = data["token"]
        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})

            test_level = decoded_token.get("level")
            test_username = decoded_token.get("username")
            if not check_token(token, test_username, cursor):
                raise ValueError("Invalid token")
            if not test_level == 0:
                raise ValueError("Unauthorized")
        except Exception:
            return jsonify({"status": "error", "message": "Invalid token"}), 401
        change_password(username, new_password, level, cursor, connection)
        return jsonify({"status": "success", "message": "Password changed"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/backupDatabase", methods=["GET"])
def backup_database() -> Tuple[Response, int]:
    """
    Handles backing up the database

    Args:
        None

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        print("Backing up database...")
        backup_data(get_db().cursor())

        return jsonify({"status": "success", "message": "Database backed up"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/restoreDatabase", methods=["GET"])
def restore_database() -> Tuple[Response, int]:
    """
    Handles restoring the database

    Args:
        file (str): the file to restore

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.args
        if not data or "file" not in data:
            raise KeyError("Missing required parameters")

        file = data["file"]
        import_csv(file)

        return jsonify({"status": "success", "message": "Database restored"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/getFiles", methods=["GET"])
def get_files() -> Tuple[Response, int]:
    """
    Handles getting the files

    Args:
        None

    Returns:
        Tuple[Response, int]: a message with possible list of files and status code
    """
    try:
        return jsonify({"status": "success", "files": get_backup_files()}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/uploadFile", methods=["POST"])
def upload_file() -> Tuple[Response, int]:
    """
    Handles uploading a file

    Args:
        file (bytes): the file to upload

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.files
        if not data or "file" not in data:
            raise KeyError("Missing required parameters")

        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename or "uploaded_file.csv")
        file_path = os.path.join("../data", filename)

        # Read the content BEFORE saving
        file_contents = uploaded_file.read().decode("utf-8")

        # Save the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_contents)

        file_path = convert_file(file_path)

        import_csv(file_path)

        return jsonify({"status": "success", "message": "File uploaded"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/appendFile", methods=["POST"])
def append_file() -> Tuple[Response, int]:
    """
    Handles uploading a file

    Args:
        file (bytes): the file to upload

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        print("Appending file...")
        data = request.files
        if not data or "file" not in data:
            raise KeyError("Missing required parameters")

        uploaded_file = request.files["file"]

        # Directly wrap the file stream in TextIOWrapper
        file_stream = io.TextIOWrapper(uploaded_file.stream, encoding="utf-8")

        add_from_csv(file_stream)
        return jsonify({"status": "success", "message": "File uploaded"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/downloadFile", methods=["GET"])
def download_file() -> Tuple[Response, int]:
    """
    Handles downloading a file

    Args:
        fileName (str): the name of the file to download

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        # Get the query parameters from the request
        file_name = request.args.get("fileName")

        if not file_name:
            raise KeyError("Missing required 'fileName' parameter")

        # Check if the file exists
        if not os.path.exists(file_name):
            raise FileNotFoundError("File not found")

        with open(file_name, "rb") as file:
            file_content = file.read()

        # Create a BytesIO object to hold the file content in memory
        blob = BytesIO(file_content)
        blob.seek(0)  # Make sure the pointer is at the start of the file

        # Send the file as an attachment
        return (
            send_file(
                blob,  # Send the in-memory file
                as_attachment=True,  # This ensures it gets downloaded as a file
                download_name=file_name,
            ),
            200,
        )

    except Exception as e:
        return handle_exceptions(e)


@app.route("/get_log", methods=["GET"])
def get_log() -> Tuple[Response, int]:
    """
    Handles getting the log files contents

    Args:
        None

    Returns:
        Tuple[Response, int]: a message with possible log contents and status code
    """
    try:
        log_contents = ""
        for file in os.listdir("../logs"):
            with open(f"../logs/{file}", "r", encoding="utf-8") as f:
                print(f"Reading log file: {file}")
                log_contents += f.read()

        return jsonify({"status": "success", "log": log_contents}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/checkToken", methods=["POST"])
def check_auth_token() -> Tuple[Response, int]:
    """
    Handles checking the auth token

    Args:
        token (str): the token to check

    Returns:
        Tuple[Response, int]: a message with possible level and status code
    """
    try:
        data = request.json
        if data is None or "token" not in data:
            raise KeyError("missing required parameters")
        level = jwt.decode(data["token"], options={"verify_signature": False}).get(
            "level"
        )
        return jsonify({"status": "success", "level": level}), 200

    except Exception as e:
        return handle_exceptions(e)


@app.route("/getUsers", methods=["GET"])
def fetch_users() -> Tuple[Response, int]:
    """
    Handles getting the users

    Args:
        None

    Returns:
        Tuple[Response, int]: a message with possible users and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        users = get_users(cursor)
        return jsonify({"status": "success", "users": users}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/deleteUser", methods=["POST"])
def delete_user_route() -> Tuple[Response, int]:
    """
    Handles deleting a user

    Args:
        username (str): the username of the user
        token (str): the cookie of the user

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.json
        connection = get_db()
        cursor = connection.cursor()
        if data is None or "username" not in data or "token" not in data:
            raise KeyError("missing required parameters")
        level = jwt.decode(data["token"], options={"verify_signature": False}).get(
            "level"
        )
        if level != 0:
            raise KeyError("User does not have admin privileges")
        delete_user(data["username"], cursor, connection)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return handle_exceptions(e)


def run_server() -> None:
    """
    Ensures the database is has the table for items, then runs the development server

    Args:
        None

    Returns:
        None
    """
    build_db()

    # sets up logging
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent duplicate logs in parent logger

    # Add the TimedRotatingFileHandler
    if not logger.handlers:  # Avoid adding duplicate handlers
        handler = TimedRotatingFileHandler(
            "../logs/app.log", when="W0", interval=1, backupCount=4
        )
        formatter = logging.Formatter("[%(asctime)s]:  %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
    app.run(debug=True, port=3000)  # Runs on http://localhost:3000


if __name__ == "__main__":
    pass
