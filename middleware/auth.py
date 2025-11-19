from fastapi import Header, HTTPException, status, Depends
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.base import get_db
from database.models.session import Session as SessionModel

async def verify_session(
  authorization: Optional[str] = Header(None),
  db: Session = Depends(get_db)
) -> str:
  """
  Middleware dependency to verify session_id from Bearer token

  Expected header format: Authorization: Bearer <session_id>

  Args:
    authorization: Authorization header containing Bearer token
    db: Database session

  Returns:
    session_id: Valid session identifier

  Raises:
    HTTPException: If token is missing, invalid, or expired
  """
  if not authorization:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Authorization header missing",
      headers={"WWW-Authenticate": "Bearer"}
    )

  # Check if it starts with "Bearer "
  if not authorization.startswith("Bearer "):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid authorization header format. Expected: Bearer <token>",
      headers={"WWW-Authenticate": "Bearer"}
    )

  # Extract session_id
  session_id = authorization.replace("Bearer ", "").strip()

  if not session_id:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Session ID is empty",
      headers={"WWW-Authenticate": "Bearer"}
    )

  # Validate session in database
  session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

  if not session:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid session ID",
      headers={"WWW-Authenticate": "Bearer"}
    )

  # Check if session expired
  if session.expired_at < datetime.now():
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Session expired. Please re-initialize.",
      headers={"WWW-Authenticate": "Bearer"}
    )

  return session_id
