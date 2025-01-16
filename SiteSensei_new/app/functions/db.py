import sqlite3

def initialize_db():
    conn = sqlite3.connect('project_db.db')
    c = conn.cursor()
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    # Create libraries table
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
    return result[0] if result else None  # Return user ID if authenticated, else None

def store_api_key(api_key, file_path, owner_id):
    """Store the API key and associated file path in the database, linked to a user by owner_id."""
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        c.execute("INSERT INTO libraries (api_key, file_path, owner_id) VALUES (?, ?, ?)",
                  (api_key, file_path, owner_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # API key already exists
    finally:
        conn.close()
    return True

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

def get_user_keys(owner_id):
    """Retrieve all API keys associated with a user."""
    try:
        conn = sqlite3.connect('project_db.db')
        c = conn.cursor()
        c.execute("SELECT api_key, file_path FROM libraries WHERE owner_id = ?", (owner_id,))
        result = c.fetchall()
        return result  # List of tuples (api_key, file_path)
    finally:
        conn.close()
