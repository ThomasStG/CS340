"""
This module provides API endpoints for an inventory management system.

Functions:
    teardown_db: Cleans up the connections and global variable on quit.
    run_server: Ensures the database has the required table for items,
                then runs the development server.

Endpoints:
    /addItem: Adds a new item to the database.
    /find: Returns a specific item from the database.
    /findAll: Returns all items from the database.
    /increment: Increments an item's count by `num_added`.
    /decrement: Decrements an item's count by `num_removed`.
    /remove: Deletes an item from the database.
    /fuzzyfind: Returns a list of items that are similar to the search term.
    /updateitem: Updates an item in the database.

    /register: Registers a new user.
    /trylogin: Tries to log in a user.
    /isLoggedIn: Checks if a user is logged in.
    /updateUser: Updates a user's password or access level.
    /checkToken: Checks if a token is valid.
    /getUsers: Returns a list of users.
    /deleteUser: Deletes a user.

    /backupDatabase: Backs up the database.
    /restoreDatabase: Restores the database from a backup.
    /getFiles: Returns a list of files in the database.
    /uploadFile: Uploads a file to the database.
    /appendFile: Appends a file to the database.
    /downloadFile: Downloads a file from the database.
    /getBackupFiles: Returns a list of backup files.

    /get_log: Returns a list of log entries.
"""

import io
import logging
import os
from io import BytesIO
from logging.handlers import TimedRotatingFileHandler
from typing import Tuple

from flask import Flask, Response, g, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from api import backup_data, build_db, get_backup_files, get_item
from auth_db import ensure_table
from auth_endpoints import (
    change_user_password_level,
    check_auth_token,
    check_login_state,
    delete_user_route,
    get_all_users,
    register_new_user,
    try_login,
)
from electrical_db import (
    backup_data_el,
    calculate_multiplier,
    ensure_tables,
    get_backup_files_el,
)
from electrical_endpoints import (  # update_passive_item,; update_active_item,
    electrical_add_item,
    electrical_get_tooltip,
    electrical_update_item,
    electrical_update_tooltip,
    find_active_item,
    find_below_threshold,
    find_passive_item,
    fuzzy_find_active_item,
    fuzzy_find_passive_item,
    get_backup_files_el,
    get_mult,
    remove_active_item,
    remove_passive_item,
)
from idea_endpoints import (
    add_item_idea,
    decrement_idea,
    find_all_items_idea,
    fuzzy_find_idea,
    increment_idea,
    remove_item_idea,
    single_search_idea,
    update_item_idea,
)
from utility_functions import (
    add_from_csv,
    get_db,
    handle_exceptions,
    import_csv,
    import_csv_el,
    refresh_from_csv_el,
)

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    # origins=["http://localhost:8080"],
    origins=["*"],
    methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
log = logging.getLogger("werkzeug")
log.disabled = True  # Enable CORS for Angular frontend


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


@app.route("/increment", methods=["GET"])
def increment() -> Tuple[Response, int]:
    """
    endpoint to increment an item's count
    """
    return increment_idea()


@app.route("/decrement", methods=["GET"])
def decrement() -> Tuple[Response, int]:
    """
    endpoint to decrement an item's count
    """
    return decrement_idea()


@app.route("/find", methods=["GET"])
def find() -> Tuple[Response, int]:
    """
    endpoint to find an individual item
    """
    return single_search_idea()


@app.route("/addItem", methods=["GET"])
def add_item() -> Tuple[Response, int]:
    """
    endpoint to add an item
    """
    return add_item_idea()


@app.route("/remove", methods=["GET"])
def remove() -> Tuple[Response, int]:
    """
    endpoint to remove an item
    """
    return remove_item_idea()


@app.route("/fuzzyfind", methods=["GET"])
def fuzzy_find() -> Tuple[Response, int]:
    """
    endpoint to fuzzy find items
    """
    return fuzzy_find_idea()


@app.route("/findAll", methods=["GET"])
def find_all() -> Tuple[Response, int]:
    """
    endpoint to retrieve all items
    """
    return find_all_items_idea()


@app.route("/updateitem", methods=["GET"])
def update() -> Tuple[Response, int]:
    """
    endpoint to update an item
    """
    return update_item_idea()


@app.route("/trylogin", methods=["POST"])
def attempt_login() -> Tuple[Response, int]:
    """
    endpoint to try to log in a user
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
    endpoint to check if a user is logged in
    """
    return check_login_state()


@app.route("/register", methods=["POST"])
def register() -> Tuple[Response, int]:
    """
    endpoint to register a user
    """
    return register_new_user()


@app.route("/updateUser", methods=["POST"])
def update_user() -> Tuple[Response, int]:
    """
    endpoint to update a user
    """
    return change_user_password_level()


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
        file_path = os.path.join("../data/idea_lab", filename)

        # Read the content BEFORE saving
        file_contents = uploaded_file.read().decode("utf-8")

        # Save the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_contents)

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
def check_user_token() -> Tuple[Response, int]:
    """
    endpoint to check if a token is valid
    """
    return check_auth_token()


@app.route("/getUsers", methods=["GET"])
def find_users() -> Tuple[Response, int]:
    """
    endpoint to get all users
    """
    return get_all_users()


@app.route("/deleteUser", methods=["POST"])
def delete_user_enpoint() -> Tuple[Response, int]:
    """
    endpoint to delete a user
    """
    return delete_user_route()


@app.route("/electricalAddItem", methods=["POST"])
def add_passive_el() -> Tuple[Response, int]:
    """
    endpoint to add a passive item
    """
    print("Adding passive item...")
    return electrical_add_item()


@app.route("/electricalRemovePassive", methods=["POST"])
def remove_passive_el() -> Tuple[Response, int]:
    """
    endpoint to remove a passive item
    """
    print("Removing passive item...")
    return remove_passive_item()


@app.route("/electricalRemoveActive", methods=["POST"])
def remove_active_el() -> Tuple[Response, int]:
    """
    endpoint to remove an active item
    """
    return remove_active_item()


@app.route("/electricalUpdateItem", methods=["POST"])
def update_item_el() -> Tuple[Response, int]:
    """
    endpoint to update an item
    """
    return electrical_update_item()


@app.route("/electricalFindPassive", methods=["GET"])
def find_passive_el() -> Tuple[Response, int]:
    """
    endpoint to find a passive item
    """
    return find_passive_item()


@app.route("/electricalFindActive", methods=["GET"])
def find_active_el() -> Tuple[Response, int]:
    """
    endpoint to find an active item
    """
    return find_active_item()


@app.route("/electricalFuzzyPassive", methods=["GET"])
def fuzzy_find_passive_el() -> Tuple[Response, int]:
    """
    endpoint to fuzzy find passive items
    """
    return fuzzy_find_passive_item()


@app.route("/electricalFuzzyActive", methods=["GET"])
def fuzzy_find_active_el() -> Tuple[Response, int]:
    """
    endpoint to fuzzy find active items
    """
    return fuzzy_find_active_item()


@app.route("/electricalFindBelowThreshold", methods=["POST"])
def find_below_threshold_el() -> Tuple[Response, int]:
    """
    endpoint to find items below threshold
    """
    return find_below_threshold()


@app.route("/getElectricalTooltip", methods=["GET"])
def get_tooltip_el() -> Tuple[Response, int]:
    return electrical_get_tooltip()


@app.route("/setElectricalTooltip", methods=["POST"])
def set_tooltip_el() -> Tuple[Response, int]:
    print("Updating tooltip...")
    return electrical_update_tooltip()


@app.route("/updateMultipliers", methods=["GET"])
def update_multipliers() -> Tuple[Response, int]:
    return update_mult()


@app.route("/getMultipliers", methods=["GET"])
def get_multipliers() -> Tuple[Response, int]:
    return get_mult()


@app.route("/getElectricalFiles", methods=["GET"])
def get_files_el() -> Tuple[Response, int]:
    """
    Handles getting the files

    Args:
        None

    Returns:
        Tuple[Response, int]: a message with possible list of files and status code
    """
    try:
        return jsonify({"status": "success", "files": get_backup_files_el()}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/restoreDatabaseElectrical", methods=["GET"])
def restore_database_el() -> Tuple[Response, int]:
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
        print("Restoring database...")
        refresh_from_csv_el(file)

        return jsonify({"status": "success", "message": "Database restored"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/appendFileElectrical", methods=["POST"])
def append_file_el() -> Tuple[Response, int]:
    """
    endpoint to append a file to the database
    """
    try:
        print("Appending file...")
        data = request.files
        if not data or "file" not in data:
            raise KeyError("Missing required parameters")

        uploaded_file = request.files["file"]

        # Directly wrap the file stream in TextIOWrapper
        file_stream = io.TextIOWrapper(uploaded_file.stream)

        with open("../data/electrical_lab/append.csv", "w") as f:
            f.write(file_stream.read())
        print("Appended file 2...")

        import_csv_el("../data/electrical_lab/append.csv")
        os.remove("../data/electrical_lab/append.csv")
        return jsonify({"status": "success", "message": "File uploaded"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/uploadFileElectrical", methods=["POST"])
def upload_file_el() -> Tuple[Response, int]:
    """
    endpoint to upload a file to the database
    """
    try:
        data = request.files
        if not data or "file" not in data:
            raise KeyError("Missing required parameters")

        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename or "uploaded_file.csv")
        file_path = os.path.join("../data/electrical", filename)

        # Read the content BEFORE saving
        file_contents = uploaded_file.read().decode("utf-8")

        # Save the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_contents)

        refresh_from_csv_el(file_path)

        return jsonify({"status": "success", "message": "File uploaded"}), 200
    except Exception as e:
        return handle_exceptions(e)


@app.route("/backupDatabaseElectrical", methods=["GET"])
def backup_database_el() -> Tuple[Response, int]:
    """
    Handles backing up the database

    Args:
        None

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        cursor = get_db().cursor()
        print("Backing up database...")
        backup_data_el(cursor)
        return jsonify({"status": "success", "message": "Database backed up"}), 200
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
    ensure_tables()

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
