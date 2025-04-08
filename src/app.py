"""
This module provides an API for an inventory management system.

Functions:
    get_db: Initializes a connection to the database using a global variable.
    teardown_db: Cleans up the connections and global variable on quit.
    import_csv: Deletes all items from the database and repopulates with values from a CSV file.
    add_from_csv: Adds items from a CSV file to the database.
    main: Implements a CLI-based testing environment.  # TODO: DELETE this
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
    /api/updateitem: Updates an item's information in the database.
    /api/trylogin: Attempts to log the user in.
    /api/isLoggedIn: Checks if the user is logged in.
    /api/register: Registers a new user.
    /api/changePassword: Changes the user's password.
"""

import csv
import datetime
import hashlib
import json
import logging
import os
import sqlite3

import jwt
import resend
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS

from api import (
    add_item,
    build_db,
    decrement_item,
    find_by_name,
    fzf,
    get_all,
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


def main() -> None:
    """
    A CLI testing environment for the database

    Args:
        None

    Returns:
        None
    """
    con = sqlite3.connect("../data/data.db")
    cur = con.cursor()
    cur.execute("""SELECT * FROM items""")
    print(cur.fetchall())
    while True:
        choice = input(
            """1. Search for item by id\n
    2. increment item by id\n
    3. decrement item by id\n
    4. Add item
    \n5. Remove item\n
    6. search item by name\n
    0. exit\n"""
        )
        match choice:
            case 0:
                cur.close()
                return
            case 1:
                val = int(input("enter the id: "))
                print(get_item(val, cur))
            case 2:
                val = int(input("enter the id: "))
                count = int(input("how many to add? "))
                increment_item(val, count, cur, con)
            case 3:
                val = int(input("enter the id: "))
                count = int(input("how many to remove? "))
                decrement_item(val, count, cur, con)
            case 4:
                name = input("enter the name: ")
                size = input("enter the size: ")
                is_metric = (
                    input("Is it metric? (True/False): ").strip().lower() == "true"
                )
                location = input("enter the location: ")
                count = int(input("enter the count: "))
                threshold = int(input("enter the low threshold: "))
                add_item(name, size, is_metric, location, count, threshold, cur, con)
            case 5:
                val = int(input("enter the id: "))
                remove_item(val, cur, con)
            case 6:
                name = input("name: ")
                is_metric = (
                    input("Is it metric? (True/False): ").strip().lower() == "true"
                )
                size = input("size: ")
                item_id = find_by_name(name, is_metric, size, cur)
                print("id = ", item_id)
                print(get_item(item_id, cur))


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
    load_dotenv("../data/.env")
    SECRET_KEY = os.environ.get("Login_Token_Secret_Key")
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
    con = sqlite3.connect("../data/data.db")
    cur = con.cursor()
    cur.execute(
        """DELETE FROM items"""
    )  # delete all items so only csv data is in the database

    # open csv file and read the data into the database
    with open(uri, newline="", encoding="utf-8") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            add_item(
                row[1],
                row[2],
                row[3] == "1",
                row[4],
                int(row[5]),
                int(row[6]),
                cur,
                con,
            )
    con.commit()


def add_from_csv(uri) -> None:
    """
    Adds values from a CSV file to the database

    Args:
        uri (str): the filepath to the CSV file

    Returns:
        None
    """
    with sqlite3.connect("../data/data.db") as con:
        cur = con.cursor()

        # open csv file and read the data into the database
        with open(uri, newline="", encoding="utf-8") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
            for row in spamreader:
                if len(row) < 7:  # Ensure the row has enough columns
                    print(f"Skipping malformed row: {row}")
                    continue

                try:
                    add_item(
                        row[1],
                        row[2],
                        row[3].strip().lower() == "true",
                        row[4],
                        int(row[5]),  # Convert safely
                        int(row[6]),
                        cur,
                        con,
                    )
                except ValueError:
                    print(f"Skipping row due to invalid integer values: {row}")
                    continue

        con.commit()  # Ensure all changes are committed


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

    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(key in data for key in ["name", "is_metric", "size", "num"]):
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

    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(key in data for key in ["name", "is_metric", "size", "num"]):
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
    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(
        key in data
        for key in ["name", "is_metric", "size", "num", "threshold", "location"]
    ):
        raise KeyError("Missing required parameters")

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
    logger = logging.getLogger(__name__)
    if not data or not all(key in data for key in ["name", "is_metric", "size"]):
        raise KeyError("Missing required parameters")

    try:
        logger.info(
            f"""Searching for item with
            name: {data['name']},
            is_metric: {data['is_metric']},
            size: {data['size']}"""
        )
        metric_val = data["is_metric"].strip().lower() == "true"
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
        # if check_token(token, username, cursor):
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


#assume user is logged in as Admin and the token is valid
@app.route("/changePassword", methods=["POST"])
def change_pass(username: str, old_password: str, new_password: str) -> jsonify:
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
            and "token" not in data
        ):
            raise KeyError("Missing required parameters")
        else:
            username = data["username"]
            old_password = data["old_password"]
            new_password = data["new_password"]
            token = data["token"]
            try:
                username = jwt.decode(token, options={"verify_signature": False}).get(
                    "username"
                )
                level = jwt.decode(token, options={"verify_signature": False}).get(
                    "level"
                )
                if not check_token(token, username, cursor):
                    raise Exception("Invalid token")
                if level > 0:
                    return jsonify({"status": "error", "message": "Unauthorized"}), 401
            
                connection = get_db()
                cursor = connection.cursor()
                change_password(username, old_password, new_password, cursor, connection)
                return jsonify({"status": "success", "message": "Password changed."}), 200
            
            except Exception as e:
                return handle_exceptions(e)
    except Exception as e:
        return handle_exceptions(e)

@app.route("/changeAccessLevel", methods=["POST"])
def change_accessLevel(username: str, accessLevel: int) -> None:
    """
    Changes the access level of a user

    Args:
        username (str): the username of the user
        accessLevel (int): the new access level of the user

    Returns:
        None
    """
    try: 
        data = request.json #POST request
        if (
            data and "username" not in data and "accessLevel" not in data and "token" not in data 
            ):
            raise KeyError("Missing required parameters")
        try:
            connection = get_db()
            cursor = connection.cursor()
            # check if the token is valid
            token = data["token"]
            username = jwt.decode(token, options={"verify_signature": False}).get(
            "username"
            )
            accessLevel = jwt.decode(token, options={"verify_signature": False}).get("Level")
            if not check_token(token, username, cursor):
                raise Exception("Invalid token")
            if accessLevel > 0:
                return jsonify({"status": "error", "message": "Unauthorized"}), 401
            
            change_accessLevel(username, accessLevel, cursor, connection)
            return jsonify({"status": "success", "message": "Access level changed."}), 200
        

        except Exception as e:
            return handle_exceptions(e)
        


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
