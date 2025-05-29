"""
This module provides endpoints for interacting with an
SQLite database for a user authentication and management system.
It includes functions to:
    - increment an item's count
    - decrement an item's count
    - add a new item
    - remove an item
    - find a specific item
    - find all items
    - search for similar items
    - update an item
"""

import logging
from typing import Tuple

import jwt
from dotenv import load_dotenv
import os
import resend

from flask import Response, jsonify, request

from idea_db import (
    increment_item,
    find_by_name,
    decrement_item,
    get_item,
    get_all,
    add_item,
    remove_item,
    fzf,
    update_item,
)
from auth_db import check_token
from utility_functions import handle_exceptions, get_db, parse_location_to_list


def increment_idea() -> Tuple[Response, int]:
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


def decrement_idea() -> Tuple[Response, int]:
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
                        "to": "j.vincent1@snhu.edu",
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


def single_search_idea() -> Tuple[Response, int]:
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
        if item is None:
            raise ValueError("Item not found")

        if (
            isinstance(item, dict)
            and "loc_shelf" in item
            and item[0]["loc_shelf"] is not None
        ):
            item[0]["location"] = parse_location_to_list(item)

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


def add_item_idea() -> Tuple[Response, int]:
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


def remove_item_idea() -> Tuple[Response, int]:
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


def fuzzy_find_idea() -> Tuple[Response, int]:
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


def find_all_items_idea() -> Tuple[Response, int]:
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


def update_item_idea() -> Tuple[Response, int]:
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
