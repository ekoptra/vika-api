from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database.base import get_db
from database.models.session import Session as SessionModel
from database.models.user import User

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


async def get_current_user(
  credentials: HTTPAuthorizationCredentials = Depends(security),
  db: Session = Depends(get_db)
) -> User:
  """
  Middleware dependency to verify JWT token and get current user

  This is used for web dashboard authentication (after login)

  Expected header format: Authorization: Bearer <jwt_token>

  Args:
    credentials: HTTP Bearer credentials from Authorization header
    db: Database session

  Returns:
    User: Current authenticated user

  Raises:
    HTTPException: If token is missing, invalid, or expired
  """
  token = credentials.credentials

  if not token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token is empty",
      headers={"WWW-Authenticate": "Bearer"}
    )

  try:
    # For now, we'll use a simple approach - the token is the API key
    # In production, you should use proper JWT with secret key

    # Find user by token (treating token as API key for simplicity)
    user = db.query(User).filter(User.api_key == token).first()

    if not user:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"}
      )

    return user

  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"}
    )
