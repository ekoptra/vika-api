from fastapi import Header, HTTPException, status
from typing import Optional

async def verify_session(authorization: Optional[str] = Header(None)):
  """
  Middleware dependency to verify session_id from Bearer token
  Expected header format: Authorization: Bearer <session_id>

  Args:
    authorization: Authorization header containing Bearer token

  Returns:
    session_id: Valid session identifier

  Raises:
    HTTPException: If token is missing or invalid
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

  # TODO: Implement actual session validation logic here

  return session_id
