from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.screen.route import screen_router
from apis.auth.route import auth_router
from apis.conversation.route import conversation_router
from common.socketio import socket_app
import apis.socketio.handlers 

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

# Mount Socket.IO
app.mount("/ws", socket_app)