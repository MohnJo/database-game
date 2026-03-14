"""
init_db.py — Creates a fresh SQLite database from the schema.sql file.

Run this script whenever you want to reset the database to a clean state.
Usage: python scripts/init_db.py
"""

import sqlite3
import os

# File paths (relative to the project root)
SCHEMA_PATH = "db/schema.sql"
DB_PATH = "db/dbg.db"


def init_db():
    # Step 1: Delete the existing database if it already exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Deleted existing database: {DB_PATH}")

    # Step 2: Read the SQL schema file
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    # Step 3: Connect to SQLite — this automatically creates the new .db file
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Step 4: Execute all CREATE TABLE statements from the schema
    cursor.executescript(schema_sql)

    # Step 5: Commit the changes to save everything to disk
    connection.commit()

    # Step 6: Query the database to find out which tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()  # Returns a list of tuples, e.g. [('pokemon',), ('trade',), ...]

    # Step 7: Close the connection — good habit to always clean up
    connection.close()

    # Step 8: Print a confirmation message
    print(f"Database created: {DB_PATH}")
    print(f"Tables created ({len(tables)}):")
    for (table_name,) in tables:
        print(f"  - {table_name}")


# Only run init_db() when this script is executed directly (not when imported)
if __name__ == "__main__":
    init_db()
