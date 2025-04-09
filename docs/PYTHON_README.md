# Overview

These four modules implement an API and database interaction layer.

There are 4 files:

1. **main.py**

- This file is a development file which ensures all the packages are installed, and starts the server

2. **app.py**

- This file sets up the API endpoints

3. **api.py**

- This file contains the database interface which the app.py file utilizes

4. **auth.py**

- This file contains the authentication interface which the app.py file utilizes

# Technologies Used

This API is built using a SQLite database and Flask to serve the API endpoints.

# Dependencies

This API requires SQLite and Python 3

# Usage

To run the API, run the following command:

```bash
python main.py
```

If you encounter issues, ensure you are in a python virtual environment.

# Endpoints

## **/increment**

- **Description**: Increments an item's count in the database.
- **Parameters**:
  - name (str): The name of the item.
  - is_metric (bool): Whether the item is metric.
  - size (str): The size of the item.
  - num (int): The amount to increment by.
- **Returns**:
  - JSON object with status message.

## **/decrement**

- **Description**: Decrements an item's count in the database and sends an email alert if the threshold is reached.
- **Parameters**:
  - name (str): The name of the item.
  - is_metric (bool): Whether the item is metric.
  - size (str): The size of the item.
  - num (int): The amount to decrement by.
- **Returns**:
  - JSON object with status message.

## **/find**

- **Description**: Finds an item in the database.
- **Parameters**:
  - name (str): The name of the item.
  - is_metric (bool): Whether the item is metric.
  - size (str): The size of the item.
- **Returns**:
  - JSON object with item details if found.

## **/add**

- **Description**: Adds a new item to the database.
- **Parameters**:
  - name (str): The name of the item.
  - is_metric (bool): Whether the item is metric.
  - size (str): The size of the item.
  - num (int): The current count of the item.
  - threshold (int): The threshold before an alert is sent.
  - location (str): The item's location.
- **Returns**:
  - JSON object with status message.

## **/remove**

- **Description**: Removes an item from the database.
- **Parameters**:
  - name (str): The name of the item.
  - is_metric (bool): Whether the item is metric.
  - size (str): The size of the item.
- **Returns**:
  - JSON object with status message.

## **/fuzzyfind**

- **Description**: Finds similar items in the database.
- **Parameters**:
  - name (str): The name of the item.
  - is_metric (bool): Whether the item is metric.
  - size (str): The size of the item.
- **Returns**:
  - JSON object with matching items.

## **/findAll**

- **Description**: Retrieves all items from the database.
- **Parameters**:
  - None
- **Returns**:
  - JSON object with a list of all items.

## **/trylogin**

- **Description**: Attempts to log a user in.
- **Parameters**:
  - username (str): The username of the user.
  - password (str): The hashed password of the user.
- **Returns**:
  - JSON object indicating success or failure.

## **/isLoggedIn**

- **Description**: Checks if the user is logged in
- **Parameters**:
  - token (str): the token of the user
- **Returns**:
  - JSON object indicating success or failure if the user is logged in.

## **/register**

- **Description**: register user
- **parameters**:
  - username (str): The username of the user.
  - password (str): The hashed password of the user.
- **Returns**:
  - JSON object indicating success or failure...I think

## **/changePassword**
- **Description**: change users password
- **paramaters**: 
  - username (str): the username of the user
  - token (str): the cookie of the user
  - new_password (str): the new password of the user
- **returns**:
  - JSON object: a message and status code
## **/get_log**
- **Description**: get the log
- **paramaters**:
- **returns**:
  log file and status code

## **run_server**
- **Description**: function to run the server
- **paramaters**: none
- **returns**:none