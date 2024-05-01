import sqlite3

def initialize_db():
    conn = sqlite3.connect('project_db.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS libraries
                 (api_key TEXT PRIMARY KEY, file_path TEXT)''')
    conn.commit()
    conn.close()

def store_api_key(api_key, file_path):
    conn = sqlite3.connect('project_db.db')
    c = conn.cursor()
    c.execute("INSERT INTO libraries (api_key, file_path) VALUES (?, ?)", (api_key, file_path))
    conn.commit()
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