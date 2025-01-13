import sqlite3

def initialize_db():
    conn = sqlite3.connect('project_db.db')
    c = conn.cursor()
    # Create libraries table
    c.execute('''CREATE TABLE IF NOT EXISTS libraries
                 (api_key TEXT PRIMARY KEY, file_path TEXT)''')
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect('project_db.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None  # Return True if user exists

def store_api_key(api_key, file_path):
    """Store the API key and associated file path in the database."""
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        c.execute("INSERT INTO libraries (api_key, file_path) VALUES (?, ?)", (api_key, file_path))
        conn.commit()
    finally:
        conn.close()

def get_file_path(api_key):
    """Retrieve the file path associated with the given API key from the database."""
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        c.execute("SELECT file_path FROM libraries WHERE api_key = ?", (api_key,))
        result = c.fetchone()
        return result[0] if result else None
    finally:
        conn.close()
