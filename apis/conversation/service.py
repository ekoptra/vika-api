import asyncio
import os
import uuid
import random
from pathlib import Path
from fastapi import UploadFile
from typing import Dict, Any
from sqlalchemy.orm import Session
from database.base import SessionLocal
from database.models.session import Session as SessionModel
from database.models.session_conversation import SessionConversation, ConversationRole
from common.config import AppConfig
from apis.socketio.handlers import emit_to_session

class ConversationService:

  @staticmethod
  async def process_audio(session_id: str, audio_file: UploadFile) -> Dict[str, Any]:
    """
    Process audio recording

    Args:
      session_id: Active session identifier (UUID string)
      audio_file: Uploaded audio file

    Returns:
      Dict with status and conversation_id
    """

    db = SessionLocal()

    try:
      # 1. Read audio data
      audio_data = await audio_file.read()
      audio_size = len(audio_data)

      # 2. Create upload directory if not exists
      Path(AppConfig.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

      # 3. Generate unique filename
      file_extension = Path(audio_file.filename).suffix if audio_file.filename else ".mp3"
      unique_filename = f"{uuid.uuid4()}{file_extension}"
      file_path = os.path.join(AppConfig.UPLOAD_DIR, unique_filename)

      # 4. Save audio to file system
      with open(file_path, "wb") as f:
        f.write(audio_data)

      # 5. Save conversation record to database (role='user')
      conversation = SessionConversation(
        session_id=session_id,
        role=ConversationRole.user,
        audio_path=file_path,
        audio_size=audio_size,
        response_json=None
      )

      db.add(conversation)
      db.commit()
      db.refresh(conversation)
      
      conversation_id = conversation.id

      asyncio.create_task(
        ConversationService._background_process_audio(conversation_id, session_id)
      )

      return {
        "status": True,
        "message": "Audio received and queued for processing",
        "conversation_id": conversation.id
      }

    finally:
      db.close()
      
  @staticmethod
  async def _background_process_audio(conversation_id: int, session_id: str):
    """
    Background process untuk transcript dan mapping deep-link

    Args:
      conversation_id: ID of conversation record
      session_id: Session ID for screen matching
    """

    # Simulate processing delay
    await asyncio.sleep(3)

    # TODO: Implement actual processing
    # 1. Get audio file from conversation_id
    # 2. Call speech-to-text API (e.g., Google Speech-to-Text, Whisper)
    # 3. Match transcription with keywords from screen_list
    # 4. Generate response text and audio
    # 5. Save AI response to database

    db = SessionLocal()

    try:
      # Generate dummy response with random navigation
      dummy_response = ConversationService._generate_dummy_response(db, session_id)

      # Create AI response conversation
      ai_conversation = SessionConversation(
        session_id=session_id,
        role=ConversationRole.ai,
        audio_path=None,
        audio_size=None,
        response_json=dummy_response
      )

      db.add(ai_conversation)
      db.commit()

      nav = dummy_response.get("navigation")
      if nav:
        print(f"✓ Background processing completed for conversation {conversation_id}")
        print(f"  → Navigation: {nav.get('screen_name')} ({nav.get('deep_link')})")
      else:
        print(f"✓ Background processing completed (no navigation)")

      # Emit Socket.IO event to notify client
      await emit_to_session(
        session_id=session_id,
        event='conversation_processed',
        data={
          'conversation_id': conversation_id,
          'status': 'completed',
          'result': dummy_response
        }
      )
      print(f"📤 Emitted conversation_processed event to session {session_id}")

    except Exception as e:
      print(f"✗ Error in background processing: {e}")

    finally:
      db.close()

  @staticmethod  
  def _generate_dummy_response(db: Session, session_id: str) -> Dict[str, Any]:
    """
    Generate dummy response with random navigation from user's screen_list

    Args:
      db: Database session
      session_id: Session ID (UUID string)

    Returns:
      Dict containing dummy transcription and navigation info
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
      return {
        "transcription": "No session found",
        "reply_text": "Sorry, I couldn't process your request.",
        "reply_audio_url": None,
        "navigation": None
      }

    screens = session.screen_list
    if not isinstance(screens, list) or len(screens) == 0:
      return {
        "transcription": "No screens available",
        "reply_text": "Please register your app screens first.",
        "reply_audio_url": None,
        "navigation": None
      }

    random_screen = random.choice(screens)
    screen_name = random_screen.get("screen_name", "Unknown")
    transcription = f"Take me to {screen_name}"
    reply_text = f"Sure, navigating to {screen_name}."

    return {
      "transcription": transcription,
      "reply_text": reply_text,
      "reply_audio_url": None,  # TODO: Generate audio response
      "navigation": {
        "screen_id": random_screen.get("screen_id"),
        "screen_name": random_screen.get("screen_name"),
        "deep_link": random_screen.get("deep_link"),
        "confidence": round(random.uniform(0.85, 0.98), 2)
      }
    }
