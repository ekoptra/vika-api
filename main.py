from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from apis.screen.route import screen_router
from apis.auth.route import auth_router
from apis.conversation.route import conversation_router
from apis.audio.route import audio_router
from common.socketio import sio
import apis.socketio.handlers
from pathlib import Path
import socketio

app = FastAPI(
  title="Vika API",
  description="Voice-based Navigation SDK API",
  version="1.0.0"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(screen_router)
app.include_router(conversation_router)
app.include_router(audio_router)

# Test page for Socket.IO
@app.get("/test/socket", response_class=HTMLResponse, tags=["Testing"])
async def socket_test_page():
  """
  Socket.IO test page - interactive UI to test real-time connection
  """
  html_path = Path(__file__).parent / "templates" / "socket_test.html"
  return html_path.read_text(encoding="utf-8")

# Mount Socket.IO with other_asgi_app
socket_asgi = socketio.ASGIApp(sio, other_asgi_app=app)

# Export the combined app for uvicorn
app = socket_asgi