"""
This module provides an API for an inventory management system.

Functions:
    get_db: Initializes a connection to the database using a global variable.
    teardown_db: Cleans up the connections and global variable on quit.
    import_csv: Deletes all items from the database and repopulates with values from a CSV file.
    add_from_csv: Adds items from a CSV file to the database.
    parse_location_to_string: Parses a JSON string into a location.
    parse_location_to_list: Parses a JSON string into a list.
    run_server: Ensures the database has the required table for items, then runs the development server.

Endpoints:
    /api/add: Adds a new item to the database.
    /api/find: Returns a specific item from the database.
    /api/findAll: Returns all items from the database.
    /api/increment: Increments an item's count by `num_added`.
    /api/decrement: Decrements an item's count by `num_removed`.
    /api/remove: Deletes an item from the database.
    /api/fuzzyfind: Returns a list of items that are similar to the search term.
"""

import csv
import datetime
import hashlib
import json
import logging
import os
import sqlite3

import jwt
import pandas as pd
import resend
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
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
from auth import change_password, check_token, create_account, get_salt, login

app = Flask(__name__)
CORS(
    app, supports_credentials=True, origins=["http://localhost:4200"]
)  # Enable CORS for Angular frontend


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


def handle_exceptions(exception: Exception) -> jsonify:
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


def generate_token(username: str):
    print("generate token")
    load_dotenv("../data/.env")
    SECRET_KEY = os.environ.get("Login_Token_Secret_Key")
    print(SECRET_KEY)
    payload = {
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=30),
        "username": username,
    }
    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        print(f"JWT encoding error: {e}")
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


def add_from_csv(uri) -> None:
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


def parse_location_to_list(location) -> str:
    """
    Parses a location string into json

    Args:
        location (str): a location string

    Returns:
        json: representing the same location
    """
    return json.loads(location)


@app.route("/increment", methods=["GET"])
def increment():
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
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(
        key in data for key in ["name", "is_metric", "size", "num", "token"]
    ):
        raise KeyError("Missing required parameters")
    try:
        token = data["token"]
        username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
        )

        if not check_token(token, username, cursor):
            raise ValueError("Invalid token")

    except Exception as e:
        return handle_exceptions(e)
    try:
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
def decrement():
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
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(
        key in data for key in ["name", "is_metric", "size", "num", "token"]
    ):
        raise KeyError("Missing required parameters")

    try:
        # check token
        if not check_token(data["token"], data["name"], cursor):
            raise ValueError("Invalid token")
    except Exception as e:
        return handle_exceptions(e)

    try:
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
def find_item():
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
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    logger = logging.getLogger(__name__)
    if not data or "name" not in data or "is_metric" not in data or "size" not in data:
        raise KeyError("Missing required parameters")

    try:
        logger.info(
            f"""Searching for item with
                name: {data['name']},
                is_metric: {data['is_metric']},
                size: {data['size']}"""
        )

        # convert metric_val to a bool
        metric_val = data["is_metric"].strip().lower() == "true"
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
def add():
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
    try:
        token = data["token"]
        username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
        )

        if not check_token(token, username, cursor):
            raise ValueError("Invalid token")

        logger = logging.getLogger(app)
        logger.info(
            f"User '{username}' added item with name: {data['name']}, size: {data['size']}, is_metric: {data['is_metric']}, num: {data['num']}, threshold: {data['threshold']}, location: {data['location']}"
        )

    except Exception as e:
        return handle_exceptions(e)

    try:

        add_item(
            data["name"],
            data["size"],
            data["is_metric"].strip().lower() == "true",
            parse_location_to_string(data["location"]),
            int(data["num"]),
            data["threshold"],
            cursor,
            connection,
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/remove", methods=["GET"])
def remove():
    """
    Handles removing an item from the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       is_metric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item

    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(key in data for key in ["name", "is_metric", "size"]):
        raise KeyError("Missing required parameters")

    try:
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
def fuzzy():
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
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    print(data)
    logger = logging.getLogger(__name__)
    if not data or not all(key in data for key in ["name", "is_metric", "size"]):
        raise KeyError("Missing required parameters")

    print(data)
    try:
        logger.info(
            f"""Searching for item with
            name: {data['name']},
            is_metric: {data['is_metric']},
            size: {data['size']}"""
        )
        metric_val = data["is_metric"].strip().lower() == "true"
        items = fzf(data["name"], metric_val, data["size"], cursor)
        print(items)
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
def list_all():
    """
    Handles retrieving all items in the database.
    Data is passed from frontend through a GET request

    Args:
        None

    Returns:
        json: a message, and return code, if no error occures data
    """
    connection = get_db()
    cursor = connection.cursor()
    try:

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
def update():
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
            ]
        ):
            raise KeyError("Missing required parameters")

        connection = get_db()
        cursor = connection.cursor()
        update_item(
            data["name"],
            data["size"],
            data["is_metric"].strip().lower() == "true",
            data["location"],
            data["threshold"],
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
def try_login() -> jsonify:
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
        token = login(username, hashed_password, cursor)
        if token == "":
            raise Exception("Login failed")
        return jsonify({"status": "success", "token": token}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/isLoggedIn", methods=["POST"])
def is_logged_in():
    """
    Checks if the user is logged in

    Args:
        token (str): the token of the user

    Returns:
        bool: whether the user is logged in
    """
    try:
        data = request.json
        if data is None or "token" not in data:
            raise KeyError("Missing required parameters")

        token = data["token"]
        try:
            username = jwt.decode(token, options={"verify_signature": False}).get(
                "username"
            )
        except Exception as e:
            return jsonify({"status": "error", "output": "false"}), 401
        connection = get_db()
        cursor = connection.cursor()
        if check_token(token, username, cursor):
            return jsonify({"status": "success", "output": "true"}), 200
        return jsonify({"status": "error", "output": "false"}), 401
    except Exception as e:
        return handle_exceptions(e)


@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        if (
            data
            and "username" not in data
            and "password" not in data
            and "salt" not in data
        ):
            raise KeyError("Missing required parameters")

        username = data["username"]
        password = data["password"]
        salt = data["salt"]
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
            username, hashed_password, salt.hex(), cursor, connection
        ):
            raise Exception("Login failed")
        token = generate_token(username)
        return jsonify({"status": "success", "token": token}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/changePassword", methods=["POST"])
def change_pass():
    """
    Handles changing a user's password

    Args:
        username (str): the username of the user
        old_password (str): the old password of the user
        new_password (str): the new password of the user

    Returns:
        json: a message and status code
    """
    try:
        data = request.json
        if (
            data
            and "username" not in data
            and "old_password" not in data
            and "new_password" not in data
        ):
            raise KeyError("Missing required parameters")

        username = data["username"]
        old_password = data["old_password"]
        new_password = data["new_password"]
        connection = get_db()
        cursor = connection.cursor()
        change_password(username, old_password, new_password, cursor, connection)
        return jsonify({"status": "success", "message": "Password changed"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/backupDatabase", methods=["GET"])
def backup_database():
    """
    Handles backing up the database

    Args:
        None

    Returns:
        json: a message and status code
    """
    try:
        backup_data(get_db().cursor())

        return jsonify({"status": "success", "message": "Database backed up"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/restoreDatabase", methods=["GET"])
def restore_database():
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
def get_files():
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
def upload_file():
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
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join("../data", filename)

        # Read the content BEFORE saving
        file_contents = uploaded_file.read().decode("utf-8")

        # Save the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_contents)

        # Optionally import the CSV content
        # import_csv(file_path)

        return jsonify({"status": "success", "message": "File uploaded"}), 200
    except Exception as e:
        return handle_exceptions(e)


def run_server():
    """
    Ensures the database is has the table for items, then runs the development server

    Args:
        None

    Returns:
        None
    """
    build_db()

    # sets up logging
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.basicConfig(
        filename=f"../logs/api_log.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"API server started {date}")
    app.run(debug=True, port=3000)  # Runs on http://localhost:3000


if __name__ == "__main__":
    pass
