# Name: Daniel Baez-Perez
# Date: 10/02/2026
# Assignment: Cassandra CRUD Performance Assessment
# Purpose: Perform CRUD operations on an Amazon Cassandra database.

import json
from datetime import datetime
from cassandra.cluster import Cluster

print("System Date and Time:", datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
print("Connecting to local Cassandra database...")

cluster = Cluster(["127.0.0.1"])
session = cluster.connect()

# CREATE - Amazon keyspace
session.execute("""
CREATE KEYSPACE IF NOT EXISTS Amazon
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};
""")

session.set_keyspace("amazon")

# CREATE - Reviews table
session.execute("""
CREATE TABLE IF NOT EXISTS Reviews (
    review_id text PRIMARY KEY,
    product_id text,
    reviewer_id text,
    stars int,
    review_body text,
    review_title text,
    product_category text
);
""")

# CREATE - ProductCategories table
session.execute("""
CREATE TABLE IF NOT EXISTS ProductCategories (
    product_category text,
    product_id text,
    stars int,
    language text,
    PRIMARY KEY ((product_category), product_id)
);
""")

# INSERT - JSON data
print("Importing data from file...")

with open("dataset_en_dev.json", "r", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)

        session.execute("""
        INSERT INTO Reviews (
            review_id,
            product_id,
            reviewer_id,
            stars,
            review_body,
            review_title,
            product_category
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (
            record["review_id"],
            record["product_id"],
            record["reviewer_id"],
            int(record["stars"]),
            record["review_body"],
            record["review_title"],
            record["product_category"]
        ))

        session.execute("""
        INSERT INTO ProductCategories (
            product_category,
            product_id,
            stars,
            language
        )
        VALUES (%s, %s, %s, %s);
        """, (
            record["product_category"],
            record["product_id"],
            int(record["stars"]),
            record["language"]
        ))

print("Data imported successfully!")


# READ - product category list
def display_categories():
    print("\nProduct Category List:")
    rows = session.execute(
        "SELECT DISTINCT product_category FROM ProductCategories;"
    )

    for row in rows:
        print(row)


# READ - 4 star and higher reviews
def high_star_count():
    category = input("\nEnter product category: ")

    query = """
    SELECT COUNT(*) FROM Reviews
    WHERE product_category = %s
    AND stars >= 4
    ALLOW FILTERING;
    """

    result = session.execute(query, (category,))
    print("4-star and higher review count:", result.one().count)


# READ - 1 star reviews
def low_star_count():
    category = input("\nEnter product category: ")

    query = """
    SELECT COUNT(*) FROM Reviews
    WHERE product_category = %s
    AND stars = 1
    ALLOW FILTERING;
    """

    result = session.execute(query, (category,))
    print("1-star review count:", result.one().count)


# READ - user-entered SELECT query
def custom_query():
    query = input("\nEnter a CQL SELECT statement: ").strip()

    if not query.lower().startswith("select"):
        print("Only SELECT statements are allowed.")
        return

    try:
        rows = session.execute(query)

        for row in rows:
            print(row)

    except Exception as error:
        print("Query error:", error)


# UPDATE - add/remove table columns
def modify_columns():
    print("\n1. Add a column")
    print("2. Remove a column")

    choice = input("Enter option: ")

    table = input("Enter table name (Reviews or ProductCategories): ").strip()

    if table.lower() == "reviews":
        table = "Reviews"
    elif table.lower() == "productcategories":
        table = "ProductCategories"
    else:
        print("Invalid table.")
        return

    if choice == "1":
        column = input("Enter new column name: ").strip()
        datatype = input("Enter CQL data type (text, int, etc.): ").strip()

        try:
            session.execute(
                f"ALTER TABLE {table} ADD {column} {datatype};"
            )
            print("Column added successfully!")

        except Exception as error:
            print("Error:", error)

    elif choice == "2":
        column = input("Enter column name to remove: ").strip()

        try:
            session.execute(
                f"ALTER TABLE {table} DROP {column};"
            )
            print("Column removed successfully!")

        except Exception as error:
            print("Error:", error)

    else:
        print("Invalid option.")


# DELETE - tables
def delete_tables():
    answer = input(
        "\nDelete Reviews and ProductCategories tables? (yes/no): "
    ).lower()

    if answer == "yes":
        session.execute("DROP TABLE IF EXISTS Reviews;")
        session.execute("DROP TABLE IF EXISTS ProductCategories;")
        print("Reviews and ProductCategories tables deleted.")
    else:
        print("Delete cancelled.")


# DELETE - keyspace
def delete_keyspace():
    answer = input("\nDelete Amazon keyspace? (yes/no): ").lower()

    if answer == "yes":
        session.execute("DROP KEYSPACE IF EXISTS Amazon;")
        print("Amazon keyspace deleted.")
        return True

    print("Delete cancelled.")
    return False


# MENU
while True:
    print("\nType in a number and press enter to execute the menu option.")
    print("1. Display product category list")
    print("2. Display high (4+) star review count")
    print("3. Display low (1) star review count")
    print("4. Enter a query")
    print("5. Add/Remove table columns")
    print("6. Delete tables")
    print("7. Delete keyspace")
    print("8. Exit the program")

    option = input("\nEnter option: ")

    if option == "1":
        display_categories()

    elif option == "2":
        high_star_count()

    elif option == "3":
        low_star_count()

    elif option == "4":
        custom_query()

    elif option == "5":
        modify_columns()

    elif option == "6":
        delete_tables()

    elif option == "7":
        if delete_keyspace():
            break

    elif option == "8":
        break

    else:
        print("Invalid option.")


print("\nSystem Date and Time:", datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
print("Program closed.")

cluster.shutdown()
