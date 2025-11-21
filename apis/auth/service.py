import uuid
import hmac
import hashlib
import time
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from database.base import SessionLocal
from database.models.user import User
from database.models.session import Session as SessionModel
from apis.auth.dtos.initialize import InitializeRequest
from apis.auth.dtos.register import RegisterRequest, RegisterResponse
from apis.auth.dtos.login import LoginRequest, LoginResponse
from common.config import AppConfig
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Password hasher using Argon2
ph = PasswordHasher()

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

      if AppConfig.APP_ENV == "production":
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
      if AppConfig.APP_ENV == "production":
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
      expired_at = datetime.now(timezone.utc) + timedelta(hours=24)

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

  @staticmethod
  def _hash_password(password: str) -> str:
    """
    Hash password using Argon2id
    Argon2 is more modern and secure than bcrypt, with no length limitations
    """
    return ph.hash(password)

  @staticmethod
  def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password using Argon2id
    """
    try:
      ph.verify(hashed_password, plain_password)
      return True
    except VerifyMismatchError:
      return False

  @staticmethod
  def register(request: RegisterRequest) -> RegisterResponse:
    """
    Register a new user and generate API key

    Args:
      request: Registration request with nama, email, and password

    Returns:
      RegisterResponse with user info and API key
    """
    db = SessionLocal()

    try:
      # Check if email already exists
      existing_user = db.query(User).filter(User.email == request.email).first()
      if existing_user:
        raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="Email sudah terdaftar"
        )

      # Generate API key
      api_key = f"vika_{secrets.token_urlsafe(32)}"

      # Hash password with Argon2
      hashed_password = AuthService._hash_password(request.password)

      # Create new user
      new_user = User(
        id=str(uuid.uuid4()),
        nama=request.nama,
        email=request.email,
        password=hashed_password,
        api_key=api_key
      )

      db.add(new_user)
      db.commit()
      db.refresh(new_user)

      return RegisterResponse(
        id=new_user.id,
        nama=new_user.nama,
        email=new_user.email,
        api_key=new_user.api_key
      )

    finally:
      db.close()

  @staticmethod
  def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate user and return user info with API key

    Args:
      request: Login request with email and password

    Returns:
      LoginResponse with user info and API key
    """
    db = SessionLocal()

    try:
      # Find user by email
      user = db.query(User).filter(User.email == request.email).first()

      if not user:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Email atau password salah"
        )

      # Verify password with Argon2
      if not AuthService._verify_password(request.password, user.password):
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Email atau password salah"
        )

      # Return user info and API key
      user_info = {
        "id": user.id,
        "nama": user.nama,
        "email": user.email
      }

      return LoginResponse(
        user=user_info,
        api_key=user.api_key
      )

    finally:
      db.close()
