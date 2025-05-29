"""
This module provides endpoints for interacting with the database interation file.
It includes functions to:
    - register a new user
    - try to log in a user
    - check if a user is logged in
    - update a user's password or access level
    - check if a token is valid
    - get a list of users
"""

from typing import Tuple
import hashlib
import os
import logging
import jwt
from flask import request, jsonify, Response

from auth_db import (
    create_account,
    get_salt,
    login,
    change_password,
    check_token,
    get_users,
    generate_token,
    delete_user,
)
from utility_functions import handle_exceptions, get_db


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
        logger = logging.getLogger("app")
        logger.info(f"User '{username}' logged in")
        return jsonify({"status": "success", "token": token}), 200
    except Exception as e:
        return handle_exceptions(e)


def check_login_state() -> Tuple[Response, int]:
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


def register_new_user() -> Tuple[Response, int]:
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
        connection = get_db()
        cursor = connection.cursor()
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
        if not check_token(auth_level, test_username, cursor):
            raise ValueError("Invalid token")
        if not auth_level == 0:
            raise ValueError("Unauthorized")
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


def change_user_password_level() -> Tuple[Response, int]:
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


def get_all_users() -> Tuple[Response, int]:
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
