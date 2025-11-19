from fastapi import APIRouter, HTTPException
from modules.auth.dtos.initialize import InitializeRequest, InitializeResponse
from modules.auth.service import AuthService

auth_router = APIRouter(
  prefix="/auth",
  tags=["Authentication"]
)

@auth_router.post("/initialize", response_model=InitializeResponse)
async def initialize(payload: InitializeRequest):
  """
  Initialize session with API key authentication

  This endpoint validates the API key and signature, then returns a session ID
  that can be used for subsequent requests.

  Args:
    - api_key: Your API key for authentication
    - timestamp: Current timestamp in milliseconds (for replay attack prevention)
    - signature: Request signature for verification

  Returns:
    - session_id: Unique session identifier
  """
  try:
    session_id = AuthService.initialize(payload)
    return InitializeResponse(session_id=session_id)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
