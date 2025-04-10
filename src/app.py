"""
This module provides an API for an inventory management system.

Functions:
    get_db: Initializes a connection to the database using a global variable.
    teardown_db: Cleans up the connections and global variable on quit.
    import_csv: Deletes all items from the database and repopulates with values from a CSV file.
    add_from_csv: Adds items from a CSV file to the database.
    parse_location_to_string: Parses a JSON string into a location.
    parse_location_to_list: Parses a JSON string into a list.
    run_server: Ensures the database has the required table for items,
                then runs the development server.

Endpoints:
    /api/add: Adds a new item to the database.
    /api/find: Returns a specific item from the database.
    /api/findAll: Returns all items from the database.
    /api/increment: Increments an item's count by `num_added`.
    /api/decrement: Decrements an item's count by `num_removed`.
    /api/remove: Deletes an item from the database.
    /api/fuzzyfind: Returns a list of items that are similar to the search term.
"""

import datetime
import hashlib
import json
import logging
import os
import sqlite3
from io import BytesIO
from logging.handlers import TimedRotatingFileHandler
from typing import Tuple

import jwt
import pandas as pd
import resend
from dotenv import load_dotenv
from flask import Flask, Response, g, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized
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
from auth import change_password, check_token, create_account, get_salt, login

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,  # origins=["http://localhost:4200"]
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
        g.db = sqlite3.connect("../data/data.db")
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
    load_dotenv("../data/.env")
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


def import_csv(uri: str) -> None:
    """
    Deletes all items from the database and repopulates with values from a CSV file

    Args:
        uri (str): the filepath to the CSV file

    Returns:
        None
    """
    try:
        con = sqlite3.connect("../data/data.db")
        cur = con.cursor()
        cur.execute(
            """DELETE FROM items"""
        )  # delete all items so only csv data is in the database

        # open csv file and read the data into the database
        df = pd.read_csv(uri)
        for row in df.itertuples():
            add_item(
                row.name,
                row.size,
                row.is_metric == "1",
                row.location,
                row.count,
                row.threshold,
                cur,
                con,
            )
        con.commit()
    except Exception as e:
        con.rollback()
        print(f"Error importing CSV: {e}")
    finally:
        con.close()


def add_from_csv(uri: str) -> None:
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
        df = pd.read_csv(uri)
        for row in df.itertuples():
            add_item(
                row.name,
                row.size,
                row.is_metric == "1",
                row.location,
                row.count,
                row.threshold,
                cur,
                con,
            )
        con.commit()
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


def parse_location_to_list(location: str) -> str:
    """
    Parses a location string into json

    Args:
        location (str): a location string

    Returns:
        json: representing the same location
    """
    return json.loads(location)


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
        json: a message and status code
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
            "User '{username}' incremented '{data['name']} {data['size']}' by {data['num']}"
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
        json: a message and status code
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
                load_dotenv("../data/.env")

                resend.api_key = os.getenv("Resend_API")
                _ = resend.Emails.send(
                    {
                        "from": "onboarding@resend.dev",
                        "to": "i91503647@gmail.com",
                        "subject": f"{data['name']} {data['size']} is running low!",
                        "html": f"""
                        <h2>Stock Reminder</h2>
                        <p>This is a reminder to stock up on <strong>{data['name']} {data['size']}</strong>.</p>

                        <p><strong>Current count:</strong> {data['count']}</p>""",
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
        json: a message and status code
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
            and "location" in item
            and item[0]["location"] is not None
        ):
            item[0]["location"] = parse_location_to_list(item[0]["location"])
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


@app.route("/add", methods=["GET"])
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
       location (str): the location of the item
       token (str): the cookie of the user

    Returns:
        json: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.args
        if not data or not all(
            key in data
            for key in [
                "name",
                "is_metric",
                "size",
                "num",
                "threshold",
                "location",
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
            f"User '{username}' added item with name: {data['name']}, size: {data['size']}, is_metric: {data['is_metric']}, num: {data['num']}, threshold: {data['threshold']}, location: {data['location']}"
        )

        add_item(
            data["name"],
            data["size"],
            data["is_metric"].strip().lower() == "true",
            parse_location_to_string(data["location"]),
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
        json: a message and status code
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
        username, level = jwt.decode(token, options={"verify_signature": False}).get(
            "username", "level"
        )

        if not check_token(token, username, cursor):
            raise ValueError("Invalid token")
        if level != 0:
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
       num (int): the number to increment by

    Returns:
        json: a message, and return code, if no error occures data
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
            if "location" in item and item["location"] is not None:
                item["location"] = parse_location_to_list(item["location"])
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
        json: a message, and return code, if no error occures data
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
       location (str): the location of the item
       num (int): the number to increment by
       threshold (int): the threshold of the item
       token (str): the cookie of the user

    Returns:
        json: a message and status code
    """
    try:
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
                "location",
                "threshold",
                "id",
                "count",
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
            logger.error("An unvalidated user attempted to update an item")
            return jsonify({"status": "error", "output": "false"}), 401

        connection = get_db()
        cursor = connection.cursor()
        update_item(
            data["name"],
            data["size"],
            data["is_metric"].strip().lower() == "true",
            data["location"],
            int(data["threshold"]),
            data["new_name"],
            data["new_size"],
            data["new_is_metric"].strip().lower() == "true",
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
        bool: whether the login was successful
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
        logger = logging.getLogger("app")
        logger.info(f"User '{username}' logged in")
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
        bool: whether the user is logged in
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
    try:
        data = request.json
        if (
            data
            and "username" not in data
            and "password" not in data
            and "level" not in data
        ):
            raise KeyError("Missing required parameters")

        username = data["username"]
        password = data["password"]
        level = int(data["level"])
        connection = get_db()
        cursor = connection.cursor()
        salt = os.urandom(32)

        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()

        # Update the hash object with the salt and password
        hash_object.update(salt + password.encode("utf-8"))

        # Get the hashed password as a hexadecimal string
        hashed_password = hash_object.hexdigest()

        if not create_account(
            username, level, hashed_password, salt.hex(), cursor, connection
        ):
            raise Unauthorized("Login failed")
        token = generate_token(username, level)
        return jsonify({"status": "success", "token": token}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/changePassword", methods=["POST"])
def change_pass() -> Tuple[Response, int]:
    """
    Handles changing a user's password

    Args:
        username (str): the username of the user
        token (str): the cookie of the user
        new_password (str): the new password of the user

    Returns:
        json: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.json
        if (
            data
            and "username" not in data
            and "new_password" not in data
            and "token" not in data
        ):
            raise KeyError("Missing required parameters")

        username = data["username"]
        new_password = data["new_password"]
        token = data["token"]
        try:
            username, level = jwt.decode(
                token, options={"verify_signature": False}
            ).get("username", "level")
            if not check_token(token, username, cursor):
                raise ValueError("Invalid token")
            if not level == 0:
                raise ValueError("Unauthorized")
        except Exception:
            return jsonify({"status": "error", "message": "Invalid token"}), 401
        change_password(username, new_password, cursor, connection)
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
        json: a message and status code
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
        None

    Returns:
        json: a message and status code
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
        json: a message and status code
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
        None

    Returns:
        json: a message and status code
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

        return jsonify({"status": "success", "message": "File uploaded"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/downloadFile", methods=["GET"])
def download_file() -> Tuple[Response, int]:
    """
    Handles downloading a file

    Args:
        None

    Returns:
        json: a message and status code
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
        json: a message and status code
    """
    try:
        log_contents = ""
        for file in os.listdir("../logs"):
            if file.endswith(".log"):
                with open(f"../logs/{file}", "r", encoding="utf-8") as f:
                    log_contents += f.read()

        return jsonify({"status": "success", "log": log_contents}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/checkToken", methods=["POST"])
def check_auth_token() -> Tuple[Response, int]:
    """
    Handles checking the auth token

    Args:
        None

    Returns:
        json: a message and status code
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
