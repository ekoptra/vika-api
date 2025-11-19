from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from database.base import Base

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  nama = Column(String(255), nullable=False)
  password = Column(String(255), nullable=False)
  email = Column(String(255), unique=True, nullable=False, index=True)
  api_key = Column(String(255), unique=True, nullable=False, index=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
