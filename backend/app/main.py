from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import os
from dotenv import load_dotenv

from app.routers import auth
from app.routers import conversations
from app.routers import chat

load_dotenv()

app = FastAPI(title="Parallax AI API")

# Register routers
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
