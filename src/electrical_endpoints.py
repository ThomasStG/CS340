import json
from typing import Tuple

from flask import Response, jsonify, request

from electrical_db import *
from electrical_db import (  # update_passive,; update_active,
    add_active_item_el,
    add_passive_item_el,
    calculate_multiplier,
    decrement_active_item_el,
    decrement_passive_item_el,
    get_multiplier,
    increment_active_item_el,
    increment_passive_item_el,
    remove_active_item_el,
    remove_passive_item_el,
    search_active_el,
    search_below_threshold_el,
    search_passive_el,
    search_similar_active_items_el,
    search_similar_passive_items_el,
    update_tooltip,
)
from utility_functions import get_db, handle_exceptions


def add_passive_item() -> Tuple[Response, int]:
    """
    Endpoint for adding a passive item

    Args:
        part_number (str): part number of the item
        item_type (str): type of the item
        link (str): link to the item
        value (float): value of the item
        location (str): location of the item
        rack (int): rack number of the item
        slot (str): slot of the item
        count (int): count of the item
        max_p (float): maximum power of the item
        max_v (float): maximum voltage of the item
        max_i (float): maximum current of the item
        tolerance (float): tolerance of the item
        i_hold (float): hold current of the item
        polarity (bool): polarity of the item
        seller (str): seller of the item
        dielectric_material (str): dielectric material of the item
        mounting_method (str): mounting method of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()
        if not data or not all(
            [
                "part_number" in data,
                "item_type" in data,
                "link" in data,
                "value" in data,
                "location" in data,
                "rack" in data,
                "slot" in data,
                "count" in data,
                "max_p" in data,
                "max_v" in data,
                "max_i" in data,
                "tolerance" in data,
                "i_hold" in data,
                "polarity" in data,
                "seller" in data,
                "dielectric_material" in data,
                "mounting_method" in data,
            ]
        ):
            raise KeyError("Missing required parameters")
        part_number = data["part_number"]
        item_type = data["item_type"]
        link = data["link"]
        value = data["value"]
        location = data["location"]
        rack = data["rack"]
        slot = data["slot"]
        count = data["count"]
        max_p = data["max_p"]
        max_v = data["max_v"]
        max_i = data["max_i"]
        tolerance = data["tolerance"]
        i_hold = data["i_hold"]
        polarity = data["polarity"]
        seller = data["seller"]
        dielectric_material = data["dielectric_material"]
        mounting_method = data["mounting_method"]
        connection = get_db()
        cursor = connection.cursor()
        add_passive_item_el(
            part_number=part_number,
            item_type=item_type,
            link=link,
            value=value,
            location=location,
            rack=rack,
            slot=slot,
            count=count,
            max_p=max_p,
            max_v=max_v,
            max_i=max_i,
            i_hold=i_hold,
            tolerance=tolerance,
            polarity=polarity,
            seller=seller,
            dielectric_material=dielectric_material,
            mounting_method=mounting_method,
            cursor=cursor,
            connection=connection,
        )
        return jsonify({"status": "success", "message": "Item added"}), 200
    except Exception as e:
        return handle_exceptions(e)


def add_active_item() -> Tuple[Response, int]:
    """
    Endpoint for adding an active item

    Args:
        name (str): name of the item
        part_id (str): part id of the item
        location (str): location of the item
        rack (int): rack number of the item
        slot (str): slot of the item
        count (int): count of the item
        link (str): link to the item
        description (str): description of the item
        item_type (str): type of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()
        if not data or not all(
            [
                "name" in data,
                "part_id" in data,
                "location" in data,
                "rack" in data,
                "slot" in data,
                "count" in data,
                "link" in data,
                "description" in data,
                "item_type" in data,
            ]
        ):
            raise KeyError("Missing required parameters")
        name = data["name"]
        part_id = data["part_id"]
        location = data["location"]
        rack = data["rack"]
        slot = data["slot"]
        count = data["count"]
        link = data["link"]
        description = data["description"]
        item_type = data["item_type"]
        connection = get_db()
        cursor = connection.cursor()
        add_active_item_el(
            cursor,
            connection,
            name,
            part_id,
            location,
            rack,
            slot,
            count,
            link,
            description,
            item_type,
        )
        return jsonify({"status": "success", "message": "Item added"}), 200
    except Exception as e:
        return handle_exceptions(e)


def remove_passive_item() -> Tuple[Response, int]:
    """
    Endpoint for removing a passive item

    Args:
        subtype (str): subtype of the item
        id (str): id of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()["item"]
        if not data or not all(
            [
                "subtype" in data,
                "id" in data,
            ]
        ):
            raise KeyError("Missing required parameters")
        item_type = data["subtype"]
        item_id = data["id"]
        connection = get_db()
        cursor = connection.cursor()
        remove_passive_item_el(item_type, item_id, cursor, connection)
        return jsonify({"status": "success", "message": "Item removed"}), 200
    except Exception as e:
        return handle_exceptions(e)


def remove_active_item() -> Tuple[Response, int]:
    """
    Endpoint for removing an active item

    Args:
        name (str): name of the item
        part_id (str): part id of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()
        if not data or "name" not in data and "part_id" not in data:
            raise KeyError("Missing required parameters")
        connection = get_db()
        cursor = connection.cursor()
        if "part_id" in data:
            part_id = data["part_id"]
            remove_active_item_el(
                cursor,
                connection,
                part_id,
            )
            return jsonify({"status": "success", "message": "Item removed"}), 200
        if "name" in data:
            name = data["name"]
            remove_active_item_el(cursor, connection, name)
            return jsonify({"status": "success", "message": "Item removed"}), 200
        return jsonify({"status": "success", "message": "Item removed"}), 200
    except Exception as e:
        return handle_exceptions(e)


def find_passive_item() -> Tuple[Response, int]:
    """
    Endpoint for finding a passive item

    Args:
        item_type (str): type of the item
        value (str): value of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.args
        if not data or "item_type" not in data or "value" not in data:
            raise KeyError("Missing required parameters")

        item_type = None
        value = None
        mounting_method = None
        tolerance = None

        item_type = data["item_type"]
        value = data["value"]

        if "mounting_method" in data:
            mounting_method = data["mounting_method"]
        if "tolerance" in data:
            tolerance = data["tolerance"]

        item = search_passive_el(
            cursor=get_db().cursor(),
            item_type=item_type,
            value=value,
            mounting_method=mounting_method,
            tolerance=tolerance,
        )

        return jsonify({"status": "success", "item": item}), 200
    except Exception as e:
        return handle_exceptions(e)


def find_active_item(is_assembly: bool = False) -> Tuple[Response, int]:
    """
    Endpoint for finding an active item

    Args:
        one of these must be provided
        name (str) optional: name of the item
        part_id (str) optional: part id of the item

        is_assembly (bool) optional: whether the item is an assembly

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()
        if not data or "name" not in data and "part_id" not in data:
            raise KeyError("Missing required parameters")
        if is_assembly and "subtype" in data:
            subtype = data["subtype"]
        cursor = get_db().cursor()
        if "part_id" in data:
            part_id = data["part_id"]
            return (
                jsonify(
                    {
                        "status": "success",
                        "item": search_active_el(cursor, part_id, is_assembly, subtype),
                    }
                ),
                200,
            )
        name = data["name"]
        return (
            jsonify(
                {
                    "status": "success",
                    "item": search_active_el(cursor, name, is_assembly, subtype),
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


def fuzzy_find_passive_item() -> Tuple[Response, int]:
    """
    Endpoint for fuzzy finding a passive item

    Args:
        value (str): value of the item
        tolerance (str): tolerance of the item
        mounting_method (str): mounting method of the item
        item_type (str): type of the item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.args
        if not data or "value" not in data:
            raise KeyError("Missing required parameters")
        cursor = get_db().cursor()
        value = float(data["value"])
        tolerance = data.get("tolerance", "").strip()
        if tolerance and tolerance.isnumeric():
            tolerance = float(tolerance)
        else:
            tolerance = None
        mounting_method = data.get("mounting_method", "").strip()
        if not mounting_method or mounting_method == "undefined":
            mounting_method = None
        item_type = data.get("item_type", "").strip()
        if not item_type or item_type == "undefined":
            item_type = None
        search_percent_str = data.get("search_percent", "").strip()
        if search_percent_str and search_percent_str.isnumeric():
            search_percent = float(search_percent_str)
        else:
            search_percent = 0.50

        items = search_similar_passive_items_el(
            cursor,
            value,
            search_percent,
            item_type,
            tolerance,
            mounting_method,
        )
        if items == []:
            raise Exception("No items found")

        item_index = items.index(min(items, key=lambda x: abs(x["value"] - value)))
        items_length = len(items)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": {
                        "items": items,
                        "index": item_index,
                        "length": items_length,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


def fuzzy_find_active_item(is_assembly: bool = False) -> Tuple[Response, int]:
    """
    Endpoint for fuzzy finding an active item

    Args:
        one of these must be provided
        name (str) optional: name of the item
        part_id (str) optional: part id of the item

        is_assembly (bool) optional: whether the item is an assembly

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.args
        if not data or "name" not in data and "part_id" not in data:
            raise KeyError("Missing required parameters")
        cursor = get_db().cursor()
        subtype = None
        if is_assembly and "subtype" in data:
            subtype = data["subtype"]
        if "part_id" in data:
            part_id = data["part_id"]
            return (
                jsonify(
                    {
                        "status": "success",
                        "items": search_similar_active_items_el(
                            cursor, part_id, is_assembly=is_assembly, subtype=subtype
                        ),
                    }
                ),
                200,
            )
        name = data["name"]
        return (
            jsonify(
                {
                    "status": "success",
                    "items": search_similar_active_items_el(
                        cursor, name, is_assembly=is_assembly, subtype=subtype
                    ),
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


def decrement_passive_item() -> Tuple[Response, int]:
    """
    Handles decrementing the count of a passive item

    Args:
        id (str): The id of the item
        num_to_remove (int): The number of items to remove

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()
        if not data or "id" not in data or "num_to_remove" not in data:
            raise KeyError("Missing required parameters")
        item_id = data["id"]
        num_to_remove = data["num_to_remove"]
        decrement_passive_item_el(item_id, num_to_remove, get_db().cursor(), get_db())
        return jsonify({"status": "success", "message": "Item decremented"}), 200
    except Exception as e:
        return handle_exceptions(e)


def decrement_active_item() -> Tuple[Response, int]:
    """
    Handles decrementing the count of an active item

    Args:
        name (str) optional: The name of the item
        item_id (str) optional: The id of the item
        num_to_remove (int): The number of items to remove

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        data = request.get_json()
        if not data or "num_to_remove" not in data:
            raise KeyError("Missing required parameters")
        if "name" in data:
            name = data["name"]
            num_to_remove = data["num_to_remove"]
            decrement_active_item_el(num_to_remove, cursor, connection, name)
            return jsonify({"status": "success", "message": "Item decremented"}), 200
        if "item_id" in data:
            item_id = data["item_id"]
            num_to_remove = data["num_to_remove"]
            decrement_active_item_el(num_to_remove, cursor, connection, item_id)
            return jsonify({"status": "success", "message": "Item decremented"}), 200

        raise KeyError("Missing required parameters")
    except Exception as e:
        return handle_exceptions(e)


def increment_passive_item() -> Tuple[Response, int]:
    """
    Handles incrementing the count of a passive item

    Args:
        id (str): The id of the item
        num_to_add (int): The number of items to add

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()
        if not data or "item_id" not in data or "num_to_add" not in data:
            raise KeyError("Missing required parameters")
        item_id = data["item_id"]
        num_to_add = data["num_to_add"]
        connection = get_db()
        cursor = connection.cursor()
        increment_passive_item_el(item_id, num_to_add, cursor, connection)
        return jsonify({"status": "success", "message": "Item incremented"}), 200
    except Exception as e:
        return handle_exceptions(e)


def increment_active_item() -> Tuple[Response, int]:
    """
    Handles incrementing the count of an active item

    Args:
        name (str) optional: The name of the item
        part_id (str) optional: The part id of the item
        num_to_add (int): The number of items to add

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.get_json()
        if (
            not data
            or "num_to_add" not in data
            or "name" not in data
            and "part_id" not in data
        ):
            raise KeyError("Missing required parameters")
        connection = get_db()
        cursor = connection.cursor()
        num_to_add = data["num_to_add"]

        if "part_id" in data:
            part_id = data["part_id"]
            increment_active_item_el(num_to_add, cursor, connection, part_id)
            return jsonify({"status": "success", "message": "Item incremented"}), 200

        name = data["name"]
        increment_active_item_el(num_to_add, cursor, connection, name=name)
        return jsonify({"status": "success", "message": "Item incremented"}), 200
    except Exception as e:
        return handle_exceptions(e)


def find_below_threshold() -> Tuple[Response, int]:
    """
    Endpoint for finding items below a threshold

    Args:
        threshold (int): The threshold to find items below

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.json
        if not data or "threshold" not in data:
            raise KeyError("Missing required parameters")
        threshold = data["threshold"]
        table_list = data.get("table", ["passive", "active", "assembly"])
        type_list = data.get("type", [])
        cursor = get_db().cursor()
        items = search_below_threshold_el(cursor, table_list, type_list, threshold)
        return (
            jsonify(
                {
                    "status": "success",
                    "items": items,
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


def electrical_update_tooltip() -> Tuple[Response, int]:
    """
    Endpoint for updating the tooltip

    Args:
        tooltip (str): The tooltip to update

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.json
        tooltip = data.get("tooltip", "")
        if not tooltip:
            raise KeyError("Missing required parameters")
        update_tooltip(get_db().cursor(), get_db(), tooltip)
        return jsonify({"status": "success", "message": "Tooltip updated"}), 200
    except Exception as e:
        return handle_exceptions(e)


def electrical_get_tooltip() -> Tuple[Response, int]:
    """
    Endpoint for getting the tooltip

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        return (
            jsonify({"status": "success", "tooltip": get_tooltip(get_db().cursor())}),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)


def electrical_update_item() -> Tuple[Response, int]:
    """
    Endpoint for updating an item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.json
        if not data:
            raise KeyError("Missing required parameters")
        item_type = data["type"]
        connection = get_db()
        cursor = connection.cursor()
        match item_type:
            case "active":
                item_name = data["name"]
                item_id = data["part_id"]
                new_name = data["new_name"]
                new_item_id = data["new_part_id"]
                location = data["location"]
                rack = data["rack"]
                slot = data["slot"]
                count = data["count"]
                link = data["link"]
                description = data["description"]
                is_assembly = data["is_assembly"]
                try:
                    subtype = data["subtype"]
                except KeyError:
                    subtype = ""
                update_active_item_el(
                    name=item_name,
                    item_id=item_id,
                    new_name=new_name,
                    new_item_id=new_item_id,
                    location=location,
                    rack=rack,
                    slot=slot,
                    count=count,
                    link=link,
                    description=description,
                    is_assembly=is_assembly,
                    subtype=subtype,
                    cursor=cursor,
                    connection=connection,
                )
            case "passive":
                item_id = data["item_id"]
                part_number = data["part_number"]
                subtype = data["subtype"]
                link = data["link"]
                value = data["value"]
                location = data["location"]
                rack = data["rack"]
                slot = data["slot"]
                count = data["count"]
                max_p = data.get("max_p")
                if max_p is None:
                    return {"status": "error", "message": "Missing max_p"}, 400
                max_v = data["max_v"]
                max_i = data["max_i"]
                i_hold = data["i_hold"]
                tolerance = data["tolerance"]
                polarity = data["polarity"]
                seller = data["seller"]
                dielectric_material = data["dielectric_material"]
                mounting_method = data["mounting_method"]
                update_passive_item_el(
                    item_id=item_id,
                    part_number=part_number,
                    item_type=subtype,
                    link=link,
                    value=value,
                    location=location,
                    rack=rack,
                    slot=slot,
                    count=count,
                    max_p=max_p,
                    max_v=max_v,
                    max_i=max_i,
                    i_hold=i_hold,
                    tolerance=tolerance,
                    polarity=polarity,
                    seller=seller,
                    dielectric_material=dielectric_material,
                    mounting_method=mounting_method,
                    cursor=cursor,
                    connection=connection,
                )

        return jsonify({"status": "success", "message": "Item updated"}), 200
    except Exception as e:
        return handle_exceptions(e)


def electrical_add_item() -> Tuple[Response, int]:
    """
    Endpoint for adding an item

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        data = request.json
        if not data:
            raise KeyError("Missing required parameters")
        item_type = data["type"]
        connection = get_db()
        cursor = connection.cursor()
        match item_type:
            case "active":
                item_name = data["name"]
                item_id = data["part_id"]
                location = data["location"]
                rack = data["rack"]
                slot = data["slot"]
                count = data["count"]
                link = data["link"]
                description = data["description"]
                is_assembly = data["is_assembly"]
                try:
                    subtype = data["subtype"]
                except KeyError:
                    subtype = ""
                add_active_item_el(
                    name=item_name,
                    part_id=item_id,
                    location=location,
                    rack=rack,
                    slot=slot,
                    count=count,
                    link=link,
                    description=description,
                    is_assembly=is_assembly,
                    item_type=subtype,
                    cursor=cursor,
                    connection=connection,
                )
            case "passive":
                part_number = data["part_number"]
                subtype = data["subtype"]
                link = data["link"]
                value = data["value"]
                location = data["location"]
                rack = data["rack"]
                slot = data["slot"]
                count = data["count"]
                max_p = data["max_power"]
                max_v = data["max_voltage"]
                max_i = data["max_current"]
                i_hold = data["current_hold"]
                tolerance = data["tolerance"]
                polarity = data["polarity"]
                seller = data["seller"]
                dielectric_material = data["dielectric_material"]
                mounting_method = data["mounting_method"]
                add_passive_item_el(
                    part_number=part_number,
                    item_type=subtype,
                    link=link,
                    value=value,
                    location=location,
                    rack=rack,
                    slot=slot,
                    count=count,
                    max_p=max_p,
                    max_v=max_v,
                    max_i=max_i,
                    i_hold=i_hold,
                    tolerance=tolerance,
                    polarity=polarity,
                    seller=seller,
                    dielectric_material=dielectric_material,
                    mounting_method=mounting_method,
                    cursor=cursor,
                    connection=connection,
                )

        return jsonify({"status": "success", "message": "Item updated"}), 200
    except Exception as e:
        return handle_exceptions(e)


def update_mult() -> Tuple[Response, int]:
    """
    Endpoint for updating the multiplier list for the passive items

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        calculate_multiplier(cursor, connection)
        return jsonify({"status": "success", "message": "Items updated"}), 200
    except Exception as e:
        return handle_exceptions(e)


def get_mult() -> Tuple[Response, int]:
    """
    Endpoint for getting the multiplier list for the passive items

    Returns:
        Tuple[Response, int]: a message and status code
    """
    try:
        connection = get_db()
        cursor = connection.cursor()
        multiplier = get_multiplier(cursor)
        if multiplier is None:
            raise Exception("No multiplier found")

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Items updated",
                    "multiplier": multiplier,
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exceptions(e)
