from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

pages_router = APIRouter(
  tags=["Pages"]
)

# Get the templates directory (go up from pages/ to root, then into templates/)
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Landing Page
@pages_router.get("/", response_class=HTMLResponse)
async def index():
  """
  Landing page
  """
  html_path = TEMPLATES_DIR / "index.html"
  return html_path.read_text(encoding="utf-8")

# Register Page
@pages_router.get("/register", response_class=HTMLResponse)
async def register_page():
  """
  Registration page
  """
  html_path = TEMPLATES_DIR / "register.html"
  return html_path.read_text(encoding="utf-8")

# Login Page
@pages_router.get("/login", response_class=HTMLResponse)
async def login_page():
  """
  Login page
  """
  html_path = TEMPLATES_DIR / "login.html"
  return html_path.read_text(encoding="utf-8")

# API Keys Page
@pages_router.get("/api-keys", response_class=HTMLResponse)
async def api_keys_page():
  """
  API keys management page
  """
  html_path = TEMPLATES_DIR / "api-keys.html"
  return html_path.read_text(encoding="utf-8")

# Documentation Page
@pages_router.get("/documentation", response_class=HTMLResponse)
async def docs_page():
  """
  SDK Documentation page
  """
  html_path = TEMPLATES_DIR / "docs.html"
  return html_path.read_text(encoding="utf-8")

# Test page for Socket.IO
@pages_router.get("/test/socket", response_class=HTMLResponse)
async def socket_test_page():
  """
  Socket.IO test page - interactive UI to test real-time connection
  """
  html_path = TEMPLATES_DIR / "socket_test.html"
  return html_path.read_text(encoding="utf-8")