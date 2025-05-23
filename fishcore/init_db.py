import sqlite3

def initialize_database():
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()

    # Drop old tables (optional — only use in dev or if you're rebuilding everything)
    cursor.execute("DROP TABLE IF EXISTS videos")
    cursor.execute("DROP TABLE IF EXISTS lessons")
    cursor.execute("DROP TABLE IF EXISTS categories")
    cursor.execute("DROP TABLE IF EXISTS users")

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0
    )
    ''')

    # Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        icon TEXT,
        display_order INTEGER DEFAULT 0
    )
    ''')

    # Lessons table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        media_type TEXT NOT NULL,
        media_url TEXT NOT NULL,
        category_id INTEGER,
        uploaded_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')

    conn.commit()
    conn.close()

    print("✅ Database schema updated and initialized.")
