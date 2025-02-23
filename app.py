import csv
import json
import sqlite3
import sys

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from fuzzywuzzy import process

from api import (
    addItem,
    buildDB,
    decrementItem,
    findByName,
    fzf,
    getItem,
    incrementItem,
    removeItem,
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular frontend


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("data.db")
        g.db.row_factory = sqlite3.Row  # Allows dictionary-like row access
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def main():
    con = sqlite3.connect("./data.db")
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
                sys.exit(0)
            case 1:
                val = int(input("enter the id: "))
                print(getItem(val, cur))
            case 2:
                val = int(input("enter the id: "))
                count = int(input("how many to add? "))
                incrementItem(val, count, cur, con)
            case 3:
                val = int(input("enter the id: "))
                count = int(input("how many to remove? "))
                decrementItem(val, count, cur, con)
            case 4:
                name = input("enter the name: ")
                size = input("enter the size: ")
                isMetric = (
                    input("Is it metric? (True/False): ").strip().lower() == "true"
                )
                location = input("enter the location: ")
                count = int(input("enter the count: "))
                threshold = int(input("enter the low threshold: "))
                addItem(name, size, isMetric, location, count, threshold, cur, con)
            case 5:
                val = int(input("enter the id: "))
                removeItem(val, cur, con)
            case 6:
                name = input("name: ")
                isMetric = (
                    input("Is it metric? (True/False): ").strip().lower() == "true"
                )
                size = input("size: ")
                itemID = findByName(name, isMetric, size, cur)
                print("id = ", itemID)
                print(getItem(itemID, cur))


def importCSV():
    con = get_db()
    cur = con.cursor()
    cur.execute("""DELETE FROM items""")
    with open("./SampleData.csv", newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            addItem(row[1], row[2], row[3], row[4], row[5], row[6], cur, con)
    con.commit()


def parseLocationToString(location):
    return json.dumps(location)


def parseLocationToList(location):
    return json.loads(location)


@app.route("/increment", methods=["GET"])
def increment():
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if (
        not data
        or "name" not in data
        or "isMetric" not in data
        or "size" not in data
        or "num" not in data
    ):
        return jsonify({"error": "Invalid data"}), 400

    try:
        itemId = findByName(data["name"], data["isMetric"], data["size"], cursor)
        if itemId is None:
            return jsonify({"message": "Error item not found"}), 404

        incrementItem(
            itemId,
            data["num"],
            cursor,
            connection,
        )
        return jsonify({"message": "Item incremented successfully"})
    except Exception as e:
        return jsonify({"message": f"Error incrementing item: {str(e)}"}), 400


@app.route("/decrement", methods=["GET"])
def decrement():
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if (
        not data
        or "name" not in data
        or "isMetric" not in data
        or "size" not in data
        or "num" not in data
    ):
        return jsonify({"error": "Invalid data"}), 400

    try:
        itemId = findByName(data["name"], data["isMetric"], data["size"], cursor)
        if itemId is None:
            return jsonify({"message": "Error item not found"}), 404
        decrementItem(
            itemId,
            data["num"],
            cursor,
            connection,
        )

        return jsonify({"message": "Item decremented successfully"})
    except Exception as e:
        return jsonify({"message": f"Error decrementing item: {str(e)}"}), 400


@app.route("/find", methods=["GET"])
def findItem():
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or "name" not in data or "isMetric" not in data or "size" not in data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        print(
            f"Searching for item with name: {data['name']}, isMetric: {data['isMetric']}, size: {data['size']}"
        )
        metric_val = data["isMetric"].strip().lower() == "true"
        itemId = findByName(data["name"], metric_val, data["size"], cursor)
        print(itemId)
        if itemId is None:
            return jsonify({"message": "Error item not found"}), 404
        item = getItem(itemId, cursor)
        print(item)
        item["location"] = parseLocationToList(item["location"])
        return jsonify({"message": "Item found successfully", "data": [item]})
    except Exception as e:
        return jsonify({"message": f"Error finding item: {str(e)}"}), 400


@app.route("/add", methods=["GET"])
def add():
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if (
        not data
        or "name" not in data
        or "isMetric" not in data
        or "size" not in data
        or "num" not in data
        or "threshold" not in data
        or "location" not in data
    ):
        return jsonify({"error": "Invalid data"}), 400

    try:
        addItem(
            data["name"],
            data["size"],
            data["isMetric"],
            parseLocationToString(data["location"]),
            data["num"],
            data["threshold"],
            cursor,
            connection,
        )
        return jsonify({"message": "Item added successfully"})
    except Exception as e:
        return jsonify({"message": f"Error adding item: {str(e)}"}), 400


@app.route("/remove", methods=["GET"])
def remove():
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or "name" not in data or "isMetric" not in data or "size" not in data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        itemId = findByName(data["name"], data["isMetric"], data["size"], cursor)
        if itemId is None:
            return jsonify({"message": "Error item not found"}), 404
        removeItem(itemId, cursor, connection)

        return jsonify({"message": "Item removed successfully"})
    except Exception as e:
        return jsonify({"message": f"Error removing item: {str(e)}"}), 400


@app.route("/fuzzyfind", methods=["GET"])
def fuzzy():
    connection = get_db()
    cursor = connection.cursor()
    data = request.args
    if not data or "name" not in data or "isMetric" not in data or "size" not in data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        print(
            f"Searching for item with name: {data['name']}, isMetric: {data['isMetric']}, size: {data['size']}"
        )
        metric_val = data["isMetric"].strip().lower() == "true"
        item = fzf(data["name"], metric_val, data["size"], cursor)
        print(item)
        item["location"] = parseLocationToList(item["location"])
        return jsonify({"message": "Item found successfully", "data": [item]})
    except Exception as e:
        return jsonify({"message": f"Error finding item: {str(e)}"}), 400


if __name__ == "__main__":
    buildDB()
    app.run(debug=True, port=3000)  # Runs on http://localhost:3000
