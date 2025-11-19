import uuid
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from database.base import SessionLocal
from database.models.user import User
from database.models.session import Session as SessionModel
from apis.auth.dtos.initialize import InitializeRequest

class AuthService:

  @staticmethod
  def initialize(request: InitializeRequest) -> str:
    """
    Initialize and create session ID based on API key authentication

    Signature calculation:
    signature = HMAC-SHA256(api_key + timestamp, secret=api_key)
    """

    db = SessionLocal()

    try:
      # 1. Validate timestamp (prevent replay attacks)
      current_timestamp = int(time.time() * 1000)  # milliseconds
      time_diff = abs(current_timestamp - request.timestamp)

      # Allow 5 minutes difference
      if time_diff > 5 * 60 * 1000:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Request timestamp expired. Please resend with current timestamp."
        )

      # 2. Find user by API key
      user = db.query(User).filter(User.api_key == request.api_key).first()

      if not user:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Invalid API key"
        )

      # 3. Verify signature
      expected_signature = AuthService._generate_signature(
        request.api_key,
        request.timestamp
      )

      if not hmac.compare_digest(expected_signature, request.signature):
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Invalid signature"
        )

      # 4. Create new session (expire in 24 hours)
      session_id = str(uuid.uuid4())
      expired_at = datetime.now() + timedelta(hours=24)

      new_session = SessionModel(
        id=session_id,
        user_id=user.id,
        expired_at=expired_at
      )

      db.add(new_session)
      db.commit()
      db.refresh(new_session)

      # 5. Return session ID
      return session_id

    finally:
      db.close()

  @staticmethod
  def _generate_signature(api_key: str, timestamp: int) -> str:
    """
    Generate HMAC-SHA256 signature

    Formula: HMAC-SHA256(api_key + timestamp, secret=api_key)

    Args:
      api_key: User's API key
      timestamp: Request timestamp in milliseconds

    Returns:
      Hexadecimal signature string
    """
    message = f"{api_key}{timestamp}".encode('utf-8')
    secret = api_key.encode('utf-8')

    signature = hmac.new(
      secret,
      message,
      hashlib.sha256
    ).hexdigest()

    return signature
