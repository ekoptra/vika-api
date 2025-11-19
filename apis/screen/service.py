from typing import Dict, Any
from fastapi import HTTPException, status
from database.base import SessionLocal
from database.models.session import Session as SessionModel
from apis.screen.dtos.update import UpdateScreensRequest

class ScreenService:

  @staticmethod
  def update_screens(session_id: str, screens_data: UpdateScreensRequest) -> Dict[str, Any]:
    """
    Update multiple screens - menyimpan screen_list ke session

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

      # 2. Convert screens data to JSON format
      screens_json = []
      for screen in screens_data.screens:
        screens_json.append({
          "screen_id": screen.screen_id,
          "screen_name": screen.screen_name,
          "description": screen.description,
          "deep_link": screen.deep_link,
          "keywords": screen.keywords
        })

      # 3. Update session.screen_list
      session.screen_list = screens_json

      # 4. Save to database
      db.commit()
      db.refresh(session)

      return {
        "updated_screen_count": len(screens_data.screens),
        "screens": screens_json
      }

    finally:
      db.close()
