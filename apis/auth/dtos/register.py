from pydantic import BaseModel, Field, EmailStr

class RegisterRequest(BaseModel):
  nama: str = Field(..., min_length=1, max_length=255, description="Full name")
  email: EmailStr = Field(..., description="Email address")
  password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")

class RegisterResponse(BaseModel):
  id: str = Field(..., description="User ID")
  nama: str = Field(..., description="Full name")
  email: str = Field(..., description="Email address")
  api_key: str = Field(..., description="Generated API key")
