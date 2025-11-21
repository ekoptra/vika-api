from pydantic import BaseModel, Field, EmailStr

class LoginRequest(BaseModel):
  email: EmailStr = Field(..., description="Email address")
  password: str = Field(..., description="Password")

class LoginResponse(BaseModel):
  user: dict = Field(..., description="User information")
  api_key: str = Field(..., description="User's API key")
