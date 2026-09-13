import sqlite3

def create_database():
    # 1. Connect to SQLite (This automatically creates 'app_database.db' if it doesn't exist)
    conn = sqlite3.connect("app_database.db")
    cursor = conn.cursor()
    
    # 2. Read the schema.sql file
    with open("schema.sql", "r") as f:
        schema_sql = f.read()
    
    # 3. Execute the SQL script to create tables and relationships
    try:
        cursor.executescript(schema_sql)
        print("🎉 Success! 'app_database.db' created with all tables and relationships.")
    except sqlite3.Error as e:
        print(f"❌ Error creating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
