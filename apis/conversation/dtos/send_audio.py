from pydantic import BaseModel, Field

class SendAudioResponse(BaseModel):
  status: bool = Field(..., description="Status of audio reception")
  message: str = Field(..., description="Response message")
  conversation_id: int = Field(..., description="ID of created conversation record")