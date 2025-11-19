import os
import dotenv

dotenv.load_dotenv(override=True)

class AppConfig:
  DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vika_ng")
  # Normalize path untuk Windows compatibility
  UPLOAD_DIR: str = os.path.normpath(os.getenv("UPLOAD_DIR", "uploads/audio"))
  APP_ENV: str = os.getenv("APP_ENV", "development")
  