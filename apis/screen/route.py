from fastapi import APIRouter, Depends
from apis.screen.dtos.update import UpdateScreensRequest, UpdateScreensResponse
from apis.screen.service import ScreenService
from middleware.auth import verify_session

screen_router = APIRouter(
  prefix="/screen",
  tags=["Screen"]
)

@screen_router.post("/", response_model=UpdateScreensResponse)
async def update_screens(
  payload: UpdateScreensRequest,
  session_id: str = Depends(verify_session)
):
  """
  Update user's screen list

  This endpoint saves the list of screens to the user's profile.
  The screens will be used for voice navigation matching.

  Requires:
    - Authorization: Bearer <session_id>

  Args:
    payload: List of screens to update/register
    session_id: Extracted from Bearer token via middleware

  Returns:
    UpdateScreensResponse with count of updated screens
  """

  result = ScreenService.update_screens(session_id, payload)

  return UpdateScreensResponse(updated_screen_count=result['updated_screen_count'])
