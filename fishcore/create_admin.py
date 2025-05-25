# scripts/create_admin.py
from werkzeug.security import generate_password_hash
from fishcore.models import User
from fishcore.db import get_db

db = next(get_db())

admin_email = "adminBo@gmail.com"
admin_password = generate_password_hash("1")

existing = db.query(User).filter_by(email=admin_email).first()
if existing:
    print("❗ Admin user already exists.")
else:
    admin_user = User(
        email=admin_email,
        password=admin_password,
        is_admin=True
    )
    db.add(admin_user)
    db.commit()
    print("✅ Admin user created.")
