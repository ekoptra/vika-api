from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from apis.screen.route import screen_router
from apis.auth.route import auth_router
from apis.conversation.route import conversation_router
from apis.audio.route import audio_router
from common.socketio import sio
from pages.route import pages_router
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
app.include_router(pages_router)

# Mount Socket.IO with other_asgi_app
socket_asgi = socketio.ASGIApp(sio, other_asgi_app=app)

# Export the combined app for uvicorn
app = socket_asgi