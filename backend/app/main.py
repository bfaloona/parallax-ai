from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import os
from dotenv import load_dotenv

from app.dependencies import get_chat_service
from app.services import ChatService
from app.routers import auth

load_dotenv()

app = FastAPI(title="Parallax AI API")

# Register routers
app.include_router(auth.router, prefix="/api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(
    request: dict,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Minimal chat endpoint - no auth, no persistence yet"""
    message = request.get("message", "")
    return EventSourceResponse(chat_service.stream_chat_response(message))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
