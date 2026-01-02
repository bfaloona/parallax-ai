from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Parallax AI Backend",
    description="API Gateway for Parallax AI",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Root endpoint to verify the backend is running.
    """
    return {"message": "Welcome to Parallax AI API", "status": "running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Docker and monitoring.
    """
    return {"status": "ok"}
