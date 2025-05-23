from fishcore.db import engine
from fishcore.models import Base

def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created.")
