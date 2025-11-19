import os 
import dotenv

dotenv.load_dotenv(override=True)

class AppConfig:
  DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vika_ng")
  UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads/audio")
  