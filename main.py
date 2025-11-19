from fastapi import FastAPI
from modules.screen.route import screen_router
from modules.sdk.route import sdk_router
from modules.auth.route import auth_router
from modules.conversation.route import conversation_router

app = FastAPI(
  title="Vika API",
  description="Voice-based navigation SDK API",
  version="1.0.0"
)

app.include_router(auth_router)
app.include_router(screen_router)
app.include_router(conversation_router)
app.include_router(sdk_router)