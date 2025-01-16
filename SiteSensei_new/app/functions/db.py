import sqlite3

def initialize_db():
    conn = sqlite3.connect('project_db.db')
    c = conn.cursor()
    print("Executing SQL: CREATE TABLE IF NOT EXISTS users...")
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    print("Executing SQL: CREATE TABLE IF NOT EXISTS libraries...")
    c.execute('''CREATE TABLE IF NOT EXISTS libraries
                 (api_key TEXT PRIMARY KEY,
                  file_path TEXT,
                  owner_id INTEGER,
                  FOREIGN KEY(owner_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        print(f"Executing SQL: {sql} with params: ({username}, {password})")
        c.execute(sql, (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Failed to execute SQL: {sql} - Username {username} already exists.")
        return False  # Username already exists
    finally:
        conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect('project_db.db')
    c = conn.cursor()
    sql = "SELECT id FROM users WHERE username = ? AND password = ?"
    print(f"Executing SQL: {sql} with params: ({username}, {password})")
    c.execute(sql, (username, password))
    result = c.fetchone()
    conn.close()
    print(f"Query Result: {result}")
    return result[0] if result else None  # Return user ID if authenticated, else None

def store_api_key(api_key, file_path, owner_id):
    """Store the API key and associated file path in the database, linked to a user by owner_id."""
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        sql = "INSERT INTO libraries (api_key, file_path, owner_id) VALUES (?, ?, ?)"
        print(f"Executing SQL: {sql} with params: ({api_key}, {file_path}, {owner_id})")
        c.execute(sql, (api_key, file_path, owner_id))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Failed to execute SQL: {sql} - API Key {api_key} already exists.")
        return False  # API key already exists
    finally:
        conn.close()
    return True

def get_file_path(api_key):
    """Retrieve the file path associated with the given API key from the database."""
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        sql = "SELECT file_path FROM libraries WHERE api_key = ?"
        print(f"Executing SQL: {sql} with params: ({api_key},)")
        c.execute(sql, (api_key,))
        result = c.fetchone()
        print(f"Query Result: {result}")
        return result[0] if result else None
    finally:
        conn.close()

def get_user_keys(owner_id):
    """Retrieve all API keys associated with a user."""
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        sql = "SELECT api_key, file_path FROM libraries WHERE owner_id = ?"
        print(f"Executing SQL: {sql} with params: ({owner_id},)")
        c.execute(sql, (owner_id,))
        result = c.fetchall()
        print(f"Query Result: {result}")
        return result  # List of tuples (api_key, file_path)
    finally:
        conn.close()
