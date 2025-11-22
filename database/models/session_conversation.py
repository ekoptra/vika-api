from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, UUID
from database.base import Base
import enum

class ConversationRole(enum.Enum):
  user = "user"
  ai = "ai"

class SessionConversation(Base):
  __tablename__ = "session_conversations"

  id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
  session_id = Column(UUID(as_uuid=False), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
  role = Column(Enum(ConversationRole), nullable=False)
  audio_path = Column(String(500), nullable=True)
  audio_size = Column(Integer, nullable=True)
  text_transcript = Column(String, nullable=True)
  response_json = Column(JSON, nullable=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

  # Relationships
  session = relationship("Session", backref="conversations")
