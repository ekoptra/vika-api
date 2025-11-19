from fastapi import APIRouter, Depends
from modules.screen.dtos.update import UpdateScreensRequest, UpdateScreensResponse
from modules.screen.service import ScreenService
from middleware.auth import verify_session

screen_router = APIRouter(
  prefix="/screen",
  tags=["Screen"]
)

@screen_router.post("/")
async def update_screen(
  payload: UpdateScreensRequest,
  session_id: str = Depends(verify_session)
):
  """
  Update a single screen
  
  Args:
    payload: Screen data to update
    session_id: Extracted from Bearer token via middleware

  Returns:
    Status of the update operation
  """
  
  result = ScreenService.update_screens(session_id, payload)
  
  return UpdateScreensResponse(updated_screen_count=result['updated_screen_count'])
