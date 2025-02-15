import csv
import sys

from api import (
    addItem,
    connectDB,
    decrimentItem,
    findByName,
    getItem,
    incrementItem,
    removeItem,
)


def main():
    con, cur = connectDB()
    cur.execute("""SELECT * FROM items""")
    print(cur.fetchall())
    while True:
        choice = input(
            """1. Search for item by id\n
    2. increment item by id\n
    3. decriment item by id\n
    4. Add item
    \n5. Remove item\n
    6. search item by name\n
    0. exit\n"""
        )
        if choice == "0":
            cur.close()
            sys.exit(0)
        elif choice == "1":
            val = int(input("enter the id: "))
            print(getItem(val, cur))
        elif choice == "2":
            val = int(input("enter the id: "))
            count = int(input("how many to add? "))
            incrementItem(val, count, cur, con)
        elif choice == "3":
            val = int(input("enter the id: "))
            count = int(input("how many to remove? "))
            decrimentItem(val, count, cur, con)
        elif choice == "4":
            name = input("enter the name: ")
            size = input("enter the size: ")
            isMetric = input("Is it metric? (True/False): ").strip().lower() == "true"
            location = input("enter the location: ")
            count = int(input("enter the count: "))
            threshold = int(input("enter the low threshold: "))
            addItem(name, size, isMetric, location, count, threshold, cur, con)
        elif choice == "5":
            val = int(input("enter the id: "))
            removeItem(val, cur, con)
        elif choice == "6":
            name = input("name: ")
            isMetric = input("Is it metric? (True/False): ").strip().lower() == "true"
            size = input("size: ")
            itemID = findByName(name, isMetric, size, cur)
            print("id = ", itemID)
            print(getItem(itemID, cur))


def importCSV():
    con, cur = connectDB()
    con.execute("""DELETE FROM items""")
    with open("./SampleData.csv", newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            addItem(row[1], row[2], row[3], row[4], row[5], row[6], cur, con)


main()
