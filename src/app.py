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
"""

import csv
import json
import sqlite3

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
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular frontend


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
def teardown_db(exception: Exception) -> None:
    """
    Cleans up the connections and global variable on quit.

    Args:
        exception (Exception): automatically called by Flask

    Returns:
        None
    """
    db = g.pop("db", None)

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


def import_csv(uri: str) -> None:
    """
    Deletes all items from the database and repopulates with values from a CSV file

    Args:
        uri (str): the filepath to the CSV file

    Returns:
        None
    """
    con = sqlite3.connect(uri)
    cur = con.cursor()
    cur.execute("""DELETE FROM items""")
    with open(uri, newline="", encoding="utf-8") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            add_item(row[1], row[2], row[3], row[4], row[5], row[6], cur, con)
    con.commit()


def add_from_csv(uri) -> None:
    """
    Adds values from a CSV file to the database

    Args:
        uri (str): the filepath to the CSV file

    Returns:
        None
    """
    con = sqlite3.connect(uri)
    cur = con.cursor()
    with open(uri, newline="", encoding="utf-8") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            add_item(row[1], row[2], row[3], row[4], row[5], row[6], cur, con)
    con.commit()


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
       isMetric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       num (int): the number to increment by

    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(key in data for key in ["name", "isMetric", "size", "num"]):
        raise KeyError("Missing required parameters")

    try:
        item_id = find_by_name(
            data["name"],
            data["isMetric"].strip().lower() == "true",
            data["size"],
            cursor,
        )
        if item_id is None:
            return jsonify({"status": "error", "message": "Error item not found"}), 404

        increment_item(
            item_id,
            int(data["num"]),
            cursor,
            connection,
        )
        return jsonify({"status": "success"}), 200
    except KeyError as e:
        return (
            jsonify({"status": "error", "message": f"Invalid request: {str(e)}"}),
            400,
        )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    except sqlite3.OperationalError:
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}),
            500,
        )


@app.route("/decrement", methods=["GET"])
def decrement():
    """
    Handles decrementing an item count in the database.
    Data is passed from frontend through a GET request
    Additionally sends an email when a threshold is reached

    Args:
       name (str): the name of the item
       isMetric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       num (int): the number to decrement by

    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(key in data for key in ["name", "isMetric", "size", "num"]):
        raise KeyError("Missing required parameters")

    try:
        item_id = find_by_name(
            data["name"],
            data["isMetric"].strip().lower() == "true",
            data["size"],
            cursor,
        )
        if item_id is None:
            return jsonify({"status": "error", "message": "Error item not found"}), 404
        message_status = decrement_item(
            item_id,
            int(data["num"]),
            cursor,
            connection,
        )
        if message_status == 1:
            # send email
            # TODO: send email
            print("Sending Email")

        return jsonify({"status": "success"}), 200
    except KeyError as e:
        return (
            jsonify({"status": "error", "message": f"Invalid request: {str(e)}"}),
            400,
        )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    except sqlite3.OperationalError:
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}),
            500,
        )


@app.route("/find", methods=["GET"])
def find_item():
    """
    Handles finding an item the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       isMetric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item

    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or "name" not in data or "isMetric" not in data or "size" not in data:
        raise KeyError("Missing required parameters")

    try:
        print(
            f"""Searching for item with
                name: {data['name']},
                isMetric: {data['isMetric']},
                size: {data['size']}"""
        )
        metric_val = data["isMetric"].strip().lower() == "true"
        item_id = find_by_name(data["name"], metric_val, data["size"], cursor)
        print(item_id)
        if item_id is None:
            return jsonify({"status": "error", "message": "Error item not found"}), 404
        item = get_item(item_id, cursor)
        print(item)

        if "location" in item and item["location"] is not None:
            item["location"] = parse_location_to_list(item["location"])
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
    except KeyError as e:
        return (
            jsonify({"status": "error", "message": f"Invalid request: {str(e)}"}),
            400,
        )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    except sqlite3.OperationalError:
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}),
            500,
        )


@app.route("/add", methods=["GET"])
def add():
    """
    Handles adding a new item the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       isMetric (int): whether the item is metric (1) or not (0)
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
        for key in ["name", "isMetric", "size", "num", "threshold", "location"]
    ):
        raise KeyError("Missing required parameters")

    try:
        add_item(
            data["name"],
            data["size"],
            data["isMetric"].strip().lower() == "true",
            parse_location_to_string(data["location"]),
            int(data["num"]),
            data["threshold"],
            cursor,
            connection,
        )
        return jsonify({"status": "success"}), 200
    except KeyError as e:
        return (
            jsonify({"status": "error", "message": f"Invalid request: {str(e)}"}),
            400,
        )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    except sqlite3.OperationalError:
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}),
            500,
        )


@app.route("/remove", methods=["GET"])
def remove():
    """
    Handles removing an item from the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       isMetric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item

    Returns:
        json: a message and status code
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(key in data for key in ["name", "isMetric", "size"]):
        raise KeyError("Missing required parameters")

    try:
        item_id = find_by_name(
            data["name"],
            data["isMetric"].strip().lower() == "true",
            data["size"],
            cursor,
        )
        if item_id is None:
            return jsonify({"status": "error", "message": "Error item not found"}), 404
        remove_item(item_id, cursor, connection)

        return jsonify({"status": "success"}), 200
    except KeyError as e:
        return (
            jsonify({"status": "error", "message": f"Invalid request: {str(e)}"}),
            400,
        )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    except sqlite3.OperationalError:
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}),
            500,
        )


@app.route("/fuzzyfind", methods=["GET"])
def fuzzy():
    """
    Handles finding similar items in the database.
    Data is passed from frontend through a GET request

    Args:
       name (str): the name of the item
       isMetric (int): whether the item is metric (1) or not (0)
       size (str): the size of the item
       num (int): the number to increment by

    Returns:
        json: a message, and return code, if no error occures data
    """
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or not all(key in data for key in ["name", "isMetric", "size"]):
        raise KeyError("Missing required parameters")

    try:
        print(
            f"Searching for item with name: {data['name']}, isMetric: {data['isMetric']}, size: {data['size']}"
        )
        metric_val = data["isMetric"].strip().lower() == "true"
        items = fzf(data["name"], metric_val, data["size"], cursor)
        for item in items:
            if "location" in item and item["location"] is not None:
                item["location"] = parse_location_to_list(item["location"])
            # TODO: may change this to string output "true"/"false" to pass to frontend
            if item["isMetric"]:
                item["isMetric"] = 1
            else:
                item["isMetric"] = 0
        print(items)
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
    except KeyError as e:
        return (
            jsonify({"status": "error", "message": f"Invalid request: {str(e)}"}),
            400,
        )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    except sqlite3.OperationalError:
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}),
            500,
        )


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
        items = get_all(cursor)
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
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid number format"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Database integrity error"}), 400
    except sqlite3.OperationalError:
        return jsonify({"status": "error", "message": "Database operation failed"}), 500
    except Exception as e:
        return (
            jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}),
            500,
        )


def run_server():
    """
    Ensures the database is has the table for items, then runs the development server

    Args:
        None

    Returns:
        None
    """
    build_db()
    app.run(debug=True, port=3000)  # Runs on http://localhost:3000


if __name__ == "__main__":
    main()
