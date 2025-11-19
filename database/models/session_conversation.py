from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from database.base import Base
import enum

class ConversationRole(enum.Enum):
  user = "user"
  ai = "ai"

class SessionConversation(Base):
  __tablename__ = "session_conversations"

  id = Column(Integer, primary_key=True, index=True)
  session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
  role = Column(Enum(ConversationRole), nullable=False)
  audio_path = Column(String(500), nullable=True)
  audio_size = Column(Integer, nullable=True)
  response_json = Column(JSON, nullable=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

  # Relationships
  session = relationship("Session", backref="conversations")
