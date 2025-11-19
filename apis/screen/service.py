from typing import Dict, Any
from fastapi import HTTPException, status
from database.base import SessionLocal
from database.models.session import Session as SessionModel
from database.models.user import User
from apis.screen.dtos.update import UpdateScreensRequest

class ScreenService:

  @staticmethod
  def update_screens(session_id: str, screens_data: UpdateScreensRequest) -> Dict[str, Any]:
    """
    Update multiple screens - menyimpan screen_list ke user

    Args:
      session_id: Active session identifier (UUID)
      screens_data: Multiple screens data to update

    Returns:
      Dict containing summary of updates
    """

    db = SessionLocal()

    try:
      # 1. Get session from database
      session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

      if not session:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Invalid session"
        )

      # 2. Get user from session
      user = db.query(User).filter(User.id == session.user_id).first()

      if not user:
        raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="User not found"
        )

      # 3. Convert screens data to JSON format
      screens_json = []
      for screen in screens_data.screens:
        screens_json.append({
          "screen_id": screen.screen_id,
          "screen_name": screen.screen_name,
          "description": screen.description,
          "deep_link": screen.deep_link,
          "keywords": screen.keywords
        })

      # 4. Update user.screen_list
      user.screen_list = screens_json

      # 5. Save to database
      db.commit()
      db.refresh(user)

      return {
        "updated_screen_count": len(screens_data.screens),
        "screens": screens_json
      }

    finally:
      db.close()
