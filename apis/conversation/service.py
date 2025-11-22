import uuid
import random
from pathlib import Path
from fastapi import UploadFile, BackgroundTasks
from typing import Dict, Any
from sqlalchemy.orm import Session
from database.base import SessionLocal
from database.models.session import Session as SessionModel
from database.models.session_conversation import SessionConversation, ConversationRole
from common.config import AppConfig
from apis.socketio.handlers import emit_to_session
from apis.conversation.audio_processor import AudioProcessor

class ConversationService:

  @staticmethod
  async def process_audio(session_id: str, audio_file: UploadFile, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Process audio recording

    Args:
      session_id: Active session identifier (UUID string)
      audio_file: Uploaded audio file
      background_tasks: FastAPI BackgroundTasks for async processing

    Returns:
      Dict with status and conversation_id
    """

    db = SessionLocal()

    try:
      # 1. Read audio data
      audio_data = await audio_file.read()
      audio_size = len(audio_data)

      # 2. Generate unique filename with normalized path
      file_extension = Path(audio_file.filename).suffix if audio_file.filename else ".mp3"
      unique_filename = f"{uuid.uuid4()}{file_extension}"
      file_path = str(Path(AppConfig.UPLOAD_DIR) / unique_filename)

      # 3. Save audio to file system (required for processing)
      Path(AppConfig.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
      with open(file_path, "wb") as f:
        f.write(audio_data)
      
      # 4. Save conversation record to database (role='user')
      conversation = SessionConversation(
        session_id=session_id,
        role=ConversationRole.user,
        audio_path=file_path,
        audio_size=audio_size,
        response_json={}
      )

      db.add(conversation)
      db.commit()
      db.refresh(conversation)

      conversation_id = str(conversation.id)

      background_tasks.add_task(
        ConversationService._background_process_audio,
        conversation_id,
        session_id,
        file_path
      )

      return {
        "status": True,
        "message": "Audio received and queued for processing",
        "conversation_id": conversation_id
      }

    finally:
      db.close()

  @staticmethod
  async def _background_process_audio(conversation_id: str, session_id: str, audio_path: str):
    """
    Background process untuk speech-to-text, anonymization, LLM, dan TTS

    Args:
      conversation_id: ID of conversation record
      session_id: Session ID for screen matching
      audio_path: Path to the audio file
    """

    db = SessionLocal()

    try:
      # Get session data untuk screen list
      session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

      screens = session.screen_list
      if not isinstance(screens, list) or len(screens) == 0:
        print(f"⚠️ No screens available for session {session_id}")
        screens = []

      # Initialize audio processor
      processor = AudioProcessor()

      print(f"🎙️ Starting audio processing for conversation {conversation_id}")

      # Step 1: Speech to text
      print("📝 Step 1: Speech to text...")
      transcript_original = await processor.speech_to_text(audio_path)
      print(f"   Original transcript: {transcript_original}")

      # Update text_transcript in database untuk user conversation
      user_conversation = db.query(SessionConversation).filter(
        SessionConversation.id == conversation_id
      ).first()

      if user_conversation:
        user_conversation.text_transcript = transcript_original
        db.commit()
        print(f"   ✓ Updated text_transcript for conversation {conversation_id}")

      # Emit event setelah transcript selesai
      await emit_to_session(
        session_id=session_id,
        event='transcription_completed',
        data={
          'conversation_id': conversation_id,
          'transcription': transcript_original
        }
      )
      print(f"📤 Emitted transcription_completed event to session {session_id}")

      # Step 2: Anonymize PII
      print("🔒 Step 2: Anonymizing PII...")
      transcript_masked, pii_mapping = processor.anonymize_pii(transcript_original)
      print(f"   Masked transcript: {transcript_masked}")
      print(f"   PII mapping: {pii_mapping}")

      # Step 3: Mask screen data
      print("🎭 Step 3: Masking screen data...")
      masked_screens, screen_mapping = processor.mask_screen_data(screens)
      print(f"   Masked {len(masked_screens)} screens")

      # Step 3.5: Get conversation history (last 10 conversations before current one)
      print("📜 Step 3.5: Fetching conversation history...")
      conversation_history = []
      try:
        # Get last 10 conversations from this session, ordered by created_at
        # Exclude current conversation by filtering id != conversation_id
        previous_conversations = db.query(SessionConversation).filter(
          SessionConversation.session_id == session_id,
          SessionConversation.id != conversation_id
        ).order_by(SessionConversation.created_at.desc()).limit(10).all()

        # Reverse to get chronological order (oldest first)
        previous_conversations.reverse()

        for conv in previous_conversations:
          # Only include if there's actual text (not None and not empty string)
          if conv.text_transcript and conv.text_transcript.strip():
            role = "user" if conv.role == ConversationRole.user else "ai"
            conversation_history.append({
              "role": role,
              "text": conv.text_transcript
            })

        print(f"   Found {len(conversation_history)} previous messages")
      except Exception as e:
        print(f"   ⚠️ Could not fetch conversation history: {e}")
        conversation_history = []

      # Step 4: Get LLM response
      print("🤖 Step 4: Getting LLM response...")
      llm_response = await processor.get_llm_response(
        transcript_masked,
        masked_screens,
        conversation_history=conversation_history if conversation_history else None
      )
      print(f"   LLM reply: {llm_response['reply_text']}")
      print(f"   Selected screen: {llm_response['selected_screen_key']}")

      # Step 5: Unmask response text
      print("🔓 Step 5: Unmasking response...")
      reply_unmasked = processor.unmask_response(llm_response["reply_text"], pii_mapping)
      print(f"   Unmasked reply: {reply_unmasked}")

      # Step 6: Unmask screen
      selected_screen = processor.unmask_screen(
        llm_response["selected_screen_key"],
        screen_mapping
      )
      if selected_screen:
        print(f"   Selected screen: {selected_screen['screen_name']}")

      # Step 7: Generate audio response
      print("🔊 Step 7: Generating audio response...")
      reply_audio_path = await processor.text_to_speech(reply_unmasked)
      print(f"   Audio saved to: {reply_audio_path}")

      # Convert audio path to URL
      audio_filename = Path(reply_audio_path).name
      reply_audio_url = f"/audio/{audio_filename}"

      # Prepare response
      response_data = {
        "transcription": transcript_original,
        "reply_text": reply_unmasked,
        "reply_audio_url": reply_audio_url,
        "navigation": selected_screen
      }

      # Create AI response conversation with text_transcript
      ai_conversation = SessionConversation(
        session_id=session_id,
        role=ConversationRole.ai,
        audio_path=reply_audio_path,
        audio_size=None,  # Will be set later if needed
        text_transcript=reply_unmasked,
        response_json=response_data
      )

      db.add(ai_conversation)
      db.commit()

      # Log result
      if selected_screen:
        print(f"✓ Background processing completed for conversation {conversation_id}")
        print(f"  → Navigation: {selected_screen.get('screen_name')} ({selected_screen.get('deep_link')})")
      else:
        print(f"✓ Background processing completed (no navigation)")

      # Emit Socket.IO event to notify client
      await emit_to_session(
        session_id=session_id,
        event='conversation_processed',
        data={
          'conversation_id': conversation_id,
          'status': 'completed',
          'result': response_data
        }
      )
      print(f"📤 Emitted conversation_processed event to session {session_id}")

    except Exception as e:
      print(f"✗ Error in background processing: {e}")
      import traceback
      traceback.print_exc()

      # Emit error event
      try:
        await emit_to_session(
          session_id=session_id,
          event='conversation_processed',
          data={
            'conversation_id': conversation_id,
            'status': 'error',
            'error': str(e)
          }
        )
      except:
        pass

    finally:
      db.close()
