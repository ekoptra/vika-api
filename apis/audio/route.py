from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from common.config import AppConfig
import os

audio_router = APIRouter(
  prefix="/audio",
  tags=["Audio"]
)

@audio_router.get("/{filename}")
async def get_audio(filename: str):
  """
  Serve audio files

  - In development (non-production): Always returns dummy-audio.wav
  - In production: Returns the actual audio file

  Args:
    filename: Audio filename to retrieve

  Returns:
    Audio file as FileResponse
  """
  
  file_path = os.path.join(AppConfig.UPLOAD_DIR, filename)

  if not os.path.exists(file_path):
    raise HTTPException(status_code=404, detail="Audio file not found")

  return FileResponse(
    path=file_path,
    media_type="audio/mpeg",
    filename=filename
  )
