# fishcore/models.py

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from .db import Base  # ✅ Use the shared Base from db.py

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)

    # Additional profile fields
    first_name = Column(String(100))
    last_name = Column(String(100))
    birthdate = Column(String(20))  # You could also use Date if you want strict type
    phone = Column(String(20))

    # Address fields
    street = Column(String(255))
    house_number = Column(String(20))
    zip_code = Column(String(20))
    city = Column(String(100))
    country = Column(String(100))

    profile_picture = Column(String(255))  # URL or filename
    bio = Column(Text, nullable=True)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    display_order = Column(Integer, default=0)

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    media_type = Column(String(20), nullable=False)
    media_url = Column(String(512), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    uploaded_by = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
