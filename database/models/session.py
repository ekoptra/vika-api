from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from database.base import Base

class Session(Base):
  __tablename__ = "sessions"

  id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
  user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  screen_list = Column(JSON, nullable=True)
  expired_at = Column(DateTime(timezone=True), nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

  # Relationships
  user = relationship("User", backref="sessions")
