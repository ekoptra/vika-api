from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from modules.conversation.dtos.send_audio import SendAudioResponse
from modules.conversation.service import ConversationService
from middleware.auth import verify_session

conversation_router = APIRouter(
  prefix="/conversation",
  tags=["Conversation"]
)

@conversation_router.post("/", response_model=SendAudioResponse)
async def send_audio(
  audio: UploadFile = File(..., description="Audio recording file"),
  session_id: str = Depends(verify_session)
):
  """
  Send audio recording for processing
  
  Args:
    audio: Audio file (multipart/form-data)
    session_id: Extracted from Bearer token via middleware

  Returns:
    Status indicating audio was received successfully
  """

  # Validate audio file exists
  if not audio:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="No audio file provided"
    )

  allowed_types = [
    "audio/mpeg",      # mp3
    "audio/mp3",       # mp3
    "audio/wav",       # wav
    "audio/wave",      # wav
    "audio/x-wav",     # wav
    "audio/mp4",       # m4a
    "audio/m4a",       # m4a
    "audio/x-m4a",     # m4a
    "audio/ogg",       # ogg
    "audio/webm",      # webm
  ]

  if audio.content_type and audio.content_type not in allowed_types:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=f"Unsupported audio format: {audio.content_type}"
    )

  # Process audio (queued for background)
  result = await ConversationService.process_audio(session_id, audio)

  # Immediately return success
  return SendAudioResponse(**result)
