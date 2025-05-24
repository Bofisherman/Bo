# fishcore/init_db.py

from fishcore.db import engine, Base
from fishcore.models import User, Category, Lesson  # this ensures models get registered!

def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created.")
