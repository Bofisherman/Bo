import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('../videos.db')

# Update username and password for the current admin
new_username = 'managerBO'
new_password = generate_password_hash('Lb020521!')

conn.execute(
    "UPDATE users SET username = ?, password = ? WHERE username = 'admin'",
    (new_username, new_password)
)

conn.commit()
conn.close()

print("Admin user updated.")
