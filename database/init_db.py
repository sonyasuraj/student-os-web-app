"""
Database Initializer for Rate My Teacher
Builds the SQLite tables from schema.sql and populates sample data from seed_data.sql.
"""

import os
import sqlite3


def init_database():
    # 1. Find the path to the database folder
    db_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(db_dir, "schema.sql")
    seed_path = os.path.join(db_dir, "seed_data.sql")
    db_path = os.path.join(db_dir, "app_database.db")

    print("🛠️  Building database...")

    # 2. Connect to SQLite (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # 3. Create the cursor object (THIS defines 'cursor' so it's not missing!)
    cursor = conn.cursor()

    # 4. Turn on Foreign Key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 5. Read and execute schema.sql (Creates the tables)
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print("  ✅ Tables created from schema.sql")
    else:
        print(f"  ❌ Error: '{schema_path}' not found!")
        conn.close()
        return

    # 6. Read and execute seed_data.sql (Inserts the sample data)
    if os.path.exists(seed_path):
        with open(seed_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print("  ✅ Sample data inserted from seed_data.sql")
    else:
        print(
            f"  ⚠️ Warning: '{seed_path}' not found, skipping sample data insert."
        )

    # 7. Save changes and close connection
    conn.commit()
    conn.close()

    print(f"\n🎉 Success! '{db_path}' is ready to use.")


if __name__ == "__main__":
    init_database()
