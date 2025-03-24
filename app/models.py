from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# создаем модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

# создаем модель для хранения ссылок (URL)
class ShortenedURL(Base):
    __tablename__ = "shortened_urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False, unique=True)
    short_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    visit_count = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

