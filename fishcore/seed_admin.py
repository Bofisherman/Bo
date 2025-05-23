from fishcore.db import get_db
from fishcore.models import User
from werkzeug.security import generate_password_hash

def create_admin():
    db = next(get_db())

    if not db.query(User).filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("AdminPassword123"),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created")
    else:
        print("ℹ️ Admin already exists")

if __name__ == "__main__":
    create_admin()
