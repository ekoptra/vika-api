from pydantic import BaseModel, Field

class SendAudioResponse(BaseModel):
  audio_size: int = Field(..., description="Size of the received audio in bytes")
  filename: str = Field(..., description="Original filename of the uploaded audio")
  content_type: str = Field(..., description="MIME type of the uploaded audio")
  status: str = Field(..., description="Processing status of the audio")