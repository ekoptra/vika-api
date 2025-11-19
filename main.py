from fastapi import FastAPI
from apis.screen.route import screen_router
from apis.auth.route import auth_router
from apis.conversation.route import conversation_router

app = FastAPI(
  title="Vika API",
  description="Voice-based Navigation SDK API",
  version="1.0.0"
)

app.include_router(auth_router)
app.include_router(screen_router)
app.include_router(conversation_router)