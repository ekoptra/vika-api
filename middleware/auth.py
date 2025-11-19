from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database.base import get_db
from database.models.session import Session as SessionModel

# Define HTTP Bearer security scheme for Swagger
security = HTTPBearer()

async def verify_session(
  credentials: HTTPAuthorizationCredentials = Depends(security),
  db: Session = Depends(get_db)
) -> str:
  """
  Middleware dependency to verify session_id from Bearer token

  Expected header format: Authorization: Bearer <session_id>

  Args:
    credentials: HTTP Bearer credentials from Authorization header
    db: Database session

  Returns:
    session_id: Valid session identifier

  Raises:
    HTTPException: If token is missing, invalid, or expired
  """
  # Extract session_id from credentials
  session_id = credentials.credentials

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

  # Check if session expired (compare timezone-aware datetimes)
  now = datetime.now(timezone.utc)
  if session.expired_at < now:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Session expired. Please re-initialize.",
      headers={"WWW-Authenticate": "Bearer"}
    )

  return session_id
