from pydantic import BaseModel, Field

class InitializeRequest(BaseModel):
  api_key: str = Field(..., min_length=1, description="API key for authentication")
  timestamp: int = Field(..., description="Request timestamp in milliseconds")
  signature: str = Field(..., min_length=1, description="Request signature for verification")

class InitializeResponse(BaseModel):
  session_id: str = Field(..., description="Unique session identifier")
