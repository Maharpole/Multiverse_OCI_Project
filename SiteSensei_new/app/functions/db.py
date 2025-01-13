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
