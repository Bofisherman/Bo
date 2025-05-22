import sqlite3
from werkzeug.security import generate_password_hash

# Correct relative path to the real DB
conn = sqlite3.connect('videos.db')  # or adjust this if needed
cursor = conn.cursor()

hashed_password = generate_password_hash('1')

cursor.execute(
    "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
    ('Bo', hashed_password, True)
)

conn.commit()
conn.close()

print("✅ Admin user created.")