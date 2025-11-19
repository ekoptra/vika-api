from pydantic import BaseModel, Field
from typing import List

class UpdateScreenRequest(BaseModel):
  screen_id: str = Field(..., min_length=1, description="Unique screen identifier")
  screen_name: str = Field(..., min_length=1)
  description: str = Field(..., min_length=1)
  deep_link: str = Field(..., regex=r'^[a-zA-Z0-9+.-]+://.*$', description="Valid deep link URL")
  keywords: List[str] = Field(..., min_items=1)

class UpdateScreensRequest(BaseModel):
  screens: List[UpdateScreenRequest] = Field(..., min_items=1, description="List of screens to update")
  
class UpdateScreensResponse(BaseModel):
  updated_screen_count: int = Field(..., ge=0, description="Number of screens successfully updated")