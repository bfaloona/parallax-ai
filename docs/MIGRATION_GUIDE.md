# Parallax AI Migration Guide
## Poe Canvas App → FastAPI + Next.js + PostgreSQL

**Document Version:** 1.0
**Created:** January 2, 2025
**Source:** Existing Poe Canvas App (~6200 lines)
**Target:** Self-hosted FastAPI backend + Next.js frontend

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Decisions](#technology-decisions)
3. [Phase 0: Infrastructure Setup](#phase-0-infrastructure-setup)
4. [Phase 1: Minimal Round Trip](#phase-1-minimal-round-trip)
5. [Phase 2: Database & Auth](#phase-2-database--auth)
6. [Phase 3: Conversation CRUD](#phase-3-conversation-crud)
7. [Phase 4: Mode System](#phase-4-mode-system)
8. [Phase 5: Model Selection](#phase-5-model-selection)
9. [Phase 6: File Upload](#phase-6-file-upload)
10. [Phase 7: Technical Drawings](#phase-7-technical-drawings)
11. [Phase 8: UI Polish](#phase-8-ui-polish)
12. [Phase 9: Search & Export](#phase-9-search--export)
13. [Phase 10: Help System](#phase-10-help-system)
14. [Phase 11: Production Deployment](#phase-11-production-deployment)
15. [Reference: Feature Inventory](#reference-feature-inventory)
16. [Reference: System Prompts](#reference-system-prompts)
17. [Reference: Brand Guidelines](#reference-brand-guidelines)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│           NEXT.JS FRONTEND (TypeScript)             │
│  • React components, Tailwind CSS                   │
│  • Chat UI, mode selector, file upload              │
│  • Auth pages (login/register)                      │
│  • Consumes FastAPI via REST + SSE streaming        │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│           FASTAPI BACKEND (Python)                  │
│  • Auth: JWT-based authentication                   │
│  • Business logic: modes, usage tracking            │
│  • PostgreSQL via SQLAlchemy                        │
│  • Direct Anthropic API calls (streaming)           │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                    │
│  • users, conversations, messages, files            │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│            ANTHROPIC CLAUDE API                     │
│  • Claude Opus 4.5 / Sonnet 4.5 / Haiku 3.5        │
└─────────────────────────────────────────────────────┘
```

**Deployment Target:** Hetzner VPS (CPX21) + Coolify

---

## Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Backend** | FastAPI | Async, auto-docs, Pydantic validation |
| **Frontend** | Next.js 14 | React Server Components, streaming UI |
| **Database** | PostgreSQL 16 | Reliable, JSONB for flexible metadata |
| **ORM** | SQLAlchemy 2.0 | Async support, Alembic migrations |
| **Auth** | JWT tokens | Simple, stateless authentication |
| **LLM** | Anthropic API direct | Skip Langflow—prompts are stable, simpler architecture |
| **File Storage** | Local filesystem | Simple start, path to S3 later |
| **Styling** | Tailwind CSS | Matches existing design system |
| **Hosting** | Hetzner + Coolify | Low cost, Docker orchestration, SSL |

### Why No Langflow?

The 7-mode system has stable, well-documented prompts. Langflow adds:
- Another service to deploy/maintain
- Additional debugging complexity
- Latency (extra network hop)

Prompts will be stored in `backend/app/config/prompts.py`. Langflow can be added later if rapid prompt iteration becomes necessary.

---

## Phase 0: Infrastructure Setup

**Goal:** All services running locally and communicating

### 0.1 Project Structure

```
parallax-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config/
│   │   │   ├── settings.py      # Environment config
│   │   │   └── prompts.py       # Mode system prompts
│   │   ├── auth/
│   │   │   ├── router.py        # Auth endpoints
│   │   │   ├── jwt.py           # Token handling
│   │   │   └── passwords.py     # Hashing
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   └── file.py
│   │   ├── routers/
│   │   │   ├── conversations.py
│   │   │   ├── chat.py
│   │   │   ├── files.py
│   │   │   └── search.py
│   │   ├── services/
│   │   │   ├── claude.py        # Anthropic API client
│   │   │   └── usage.py         # Token tracking
│   │   └── schemas/
│   │       └── *.py             # Pydantic models
│   ├── alembic/                 # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── chat/[id]/page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── chat/
│   │   ├── sidebar/
│   │   ├── drawings/
│   │   └── ui/
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   └── auth.ts              # Auth utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

### 0.2 Docker Compose (Development)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: parallax
      POSTGRES_PASSWORD: localdev
      POSTGRES_DB: parallax_ai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U parallax"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://parallax:localdev@postgres:5432/parallax_ai
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
      CORS_ORIGINS: http://localhost:3000
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

### 0.3 Environment Variables

Create `.env.example`:

```env
# Backend
DATABASE_URL=postgresql+asyncpg://parallax:localdev@localhost:5432/parallax_ai
ANTHROPIC_API_KEY=sk-ant-api03-...
JWT_SECRET=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=http://localhost:3000
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

### 0.4 Verification Checklist

```
□ Docker and Docker Compose installed
□ Node.js 20+ installed
□ Python 3.11+ installed
□ Copy .env.example to .env and fill in values
□ Run: docker-compose up postgres
□ Verify: docker exec -it parallax-ai-postgres-1 psql -U parallax -c '\l'
   Expected: Lists "parallax_ai" database
```

### Phase 0 Complete When:
- [ ] PostgreSQL container running and accessible
- [ ] Can connect to database from host machine
- [ ] Project structure created
- [ ] Environment variables configured

---

## Phase 1: Minimal Round Trip

**Goal:** Send message → Backend → Claude → Streamed response in browser

### 1.1 Backend: FastAPI Skeleton

Create `backend/requirements.txt`:

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
anthropic==0.18.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
sse-starlette==2.0.0
```

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Parallax AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(request: dict):
    """Minimal chat endpoint - no auth, no persistence yet"""
    message = request.get("message", "")

    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-5-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": message}]
        ) as stream:
            for text in stream.text_stream:
                yield {"event": "message", "data": text}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(generate())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 1.2 Frontend: Next.js Skeleton

Initialize Next.js:

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
```

Create `frontend/app/page.tsx`:

```tsx
'use client';

import { useState } from 'react';

export default function Home() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data && data !== '[DONE]') {
              setResponse(prev => prev + data);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error: Could not connect to backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gray-900 text-white">
      <h1 className="text-2xl font-bold mb-4">Parallax AI - Round Trip Test</h1>

      <div className="max-w-2xl">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          className="w-full p-3 bg-gray-800 rounded border border-gray-700 mb-4"
          rows={3}
        />

        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-4 py-2 bg-teal-600 rounded hover:bg-teal-700 disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>

        {response && (
          <div className="mt-6 p-4 bg-gray-800 rounded">
            <h2 className="text-sm text-gray-400 mb-2">Response:</h2>
            <div className="whitespace-pre-wrap">{response}</div>
          </div>
        )}
      </div>
    </main>
  );
}
```

### 1.3 Verification

```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
python -m app.main

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev

# Terminal 3: Test backend directly
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Say hello in exactly 5 words"}'
```

### Phase 1 Complete When:
- [ ] `curl localhost:8000/health` returns `{"status": "ok"}`
- [ ] Backend streams response from Claude API
- [ ] Frontend displays streamed text incrementally
- [ ] No CORS errors in browser console

---

## Phase 2: Database & Auth

**Goal:** User registration, login, JWT-protected routes

### 2.1 Additional Dependencies

Add to `backend/requirements.txt`:

```
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
```

### 2.2 Database Models

Create `backend/app/models/base.py`:

```python
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
```

Create `backend/app/models/user.py`:

```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    tier = Column(String(20), default="free")  # free, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
```

Create `backend/app/models/conversation.py`:

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Conversation")
    current_mode = Column(String(20), default="balanced")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    mode_used = Column(String(20))
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
```

### 2.3 Auth Endpoints

Create `backend/app/auth/passwords.py`:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

Create `backend/app/auth/jwt.py`:

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRATION = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

security = HTTPBearer()

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=EXPIRATION)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return decode_token(credentials.credentials)
```

Create `backend/app/auth/router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from ..models.base import get_db
from ..models.user import User
from .passwords import hash_password, verify_password
from .jwt import create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    tier: str

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(access_token=create_token(str(user.id)))

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(access_token=create_token(str(user.id)))

@router.get("/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=str(user.id), email=user.email, tier=user.tier)
```

### 2.4 Database Migration

```bash
cd backend
alembic init alembic

# Edit alembic/env.py to use async and import models
# Edit alembic.ini to use DATABASE_URL

alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

### 2.5 Verification

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Get profile (use token from login response)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

### Phase 2 Complete When:
- [ ] Database tables created via migration
- [ ] Register endpoint creates user and returns JWT
- [ ] Login endpoint validates credentials and returns JWT
- [ ] /me endpoint returns user profile with valid JWT
- [ ] Invalid JWT returns 401

---

## Phase 3: Conversation CRUD

**Goal:** Create, list, load, delete conversations with message persistence

### 3.1 Backend: Conversation Router

Create `backend/app/routers/conversations.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..models.base import get_db
from ..models.conversation import Conversation, Message
from ..auth.jwt import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    mode: Optional[str] = "balanced"

class ConversationResponse(BaseModel):
    id: str
    title: str
    current_mode: str
    created_at: datetime
    updated_at: datetime
    message_count: int

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    mode_used: Optional[str]
    created_at: datetime

class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    current_mode: str
    created_at: datetime
    messages: List[MessageResponse]

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    return [
        ConversationResponse(
            id=str(c.id),
            title=c.title,
            current_mode=c.current_mode,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages) if c.messages else 0
        )
        for c in conversations
    ]

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    conversation = Conversation(
        user_id=user_id,
        title=request.title,
        current_mode=request.mode
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return ConversationResponse(
        id=str(conversation.id),
        title=conversation.title,
        current_mode=conversation.current_mode,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0
    )

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationDetailResponse(
        id=str(conversation.id),
        title=conversation.title,
        current_mode=conversation.current_mode,
        created_at=conversation.created_at,
        messages=[
            MessageResponse(
                id=str(m.id),
                role=m.role,
                content=m.content,
                mode_used=m.mode_used,
                created_at=m.created_at
            )
            for m in sorted(conversation.messages, key=lambda x: x.created_at)
        ]
    )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()

    return {"status": "deleted"}

@router.patch("/{conversation_id}/mode")
async def update_mode(
    conversation_id: UUID,
    request: dict,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    valid_modes = ["balanced", "challenge", "explore", "ideate", "clarify", "plan", "audit"]
    new_mode = request.get("mode")

    if new_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of: {valid_modes}")

    conversation.current_mode = new_mode
    await db.commit()

    return {"status": "updated", "mode": new_mode}
```

### 3.2 Update main.py

```python
from fastapi import FastAPI
from .auth.router import router as auth_router
from .routers.conversations import router as conversations_router

app = FastAPI(title="Parallax AI API")

# ... CORS middleware ...

app.include_router(auth_router)
app.include_router(conversations_router)
```

### Phase 3 Complete When:
- [ ] `GET /api/conversations` returns user's conversations
- [ ] `POST /api/conversations` creates new conversation
- [ ] `GET /api/conversations/{id}` returns conversation with messages
- [ ] `DELETE /api/conversations/{id}` removes conversation
- [ ] `PATCH /api/conversations/{id}/mode` updates mode
- [ ] All endpoints require valid JWT
- [ ] Users can only access their own conversations

---

## Phase 4: Mode System

**Goal:** 7 modes with distinct system prompts affecting AI behavior

### 4.1 System Prompts Config

Create `backend/app/config/prompts.py`:

```python
SHARED_GUIDELINES = """## Parallax AI System

You are a technical design assistant for engineering work across mechanical, thermal, structural, electrical, materials, and fluid systems. You operate in the Mode specified as "Current Mode" below, which defines your intellectual stance.

### Modes
The user changes Modes via the UI—not through chat. Suggest a different Mode when it would better serve their need.

| Mode | Stance | Suggest When |
|------|--------|--------------|
| **Balanced** | Direct generalist | Requirements clear, needs detailed help |
| **Challenge** | Skeptical stress-tester | Claims "ready" without validation |
| **Explore** | Neutral researcher | Asks about options or prior art |
| **Ideate** | Unconstrained generator | Stuck or repeating same approach |
| **Clarify** | Socratic questioner | Specs incomplete or conflicting |
| **Plan** | Pragmatic sequencer | Large scope, unclear next steps |
| **Audit** | Blunt feasibility analyst | Asks about cost or manufacturability |

### Technical Accuracy (Always Apply)
- Include units with appropriate significant figures
- Verify order of magnitude (mm vs m? kPa vs MPa?)
- Double-check calculations, units, and conversions
- State uncertainties clearly; don't guess at safety factors or code requirements
- Default to 2D diagrams; use 3D only when spatial relationships require it
"""

MODE_PROMPTS = {
    "balanced": """Current Mode: Balanced

Provide rigorous, direct assistance. You are the capable generalist—help without a slant. Draw on any mode's approach when it serves the user's immediate need.

**Responsibilities:** First-principles analysis, calculations with clear methodology, 2D technical drawings, design reviews (manufacturability/reliability/safety), and applicable standards.

**Process:**
- Break problems into components; show reasoning and validate assumptions
- Prioritize accuracy over speed
- Create precise 2D labeled diagrams for detailed systems; simple 3D renderings only for spatial relationships; rough 2D sketches for simple concepts""",

    "challenge": """Current Mode: Challenge

You are a skeptical adversary. Find weaknesses, poke holes, stress-test. Be constructive—you want their design to survive scrutiny, not to discourage them.

**Stance:** Assume flaws exist. Ask "what could go wrong?" Push back on assumptions, question data sources, probe edge cases. Lead with problems, not solutions.

**Process:**
- Identify the weakest assumptions first
- Propose failure modes and edge cases before offering fixes
- Use calculations to disprove or validate claims, not to assist
- State what evidence would change your assessment""",

    "explore": """Current Mode: Explore

You are a researcher. Survey what exists: prior art, standards, materials, methods, competing approaches. Ground the user in context before they commit.

**Stance:** Breadth over depth. Present options and trade-offs without advocating. Let the user decide with full context.

**Process:**
- Start with "what already exists?" before analyzing specifics
- Present 3-5 options with trade-offs, not one recommendation
- Cite standards, materials, and methods by name
- Use 2D comparison tables and diagrams when evaluating alternatives""",

    "ideate": """Current Mode: Ideate

You are a creative generator. Produce ideas freely, suspend constraints, explore the unexpected. Quantity and novelty over feasibility.

**Stance:** "What if?" thinking. Defer judgment. Combine unexpected approaches. Go beyond stated constraints—they may be artificial.

**Process:**
- Generate multiple divergent options before converging
- Defer feasibility analysis to other modes
- Use rough 2D sketches to convey concepts quickly
- Say "yes, and..." more than "but...\"""",

    "clarify": """Current Mode: Clarify

You are a Socratic coach. Ask questions instead of giving answers. Help the user sharpen their own thinking by surfacing assumptions, contradictions, and gaps.

**Stance:** Curiosity over expertise. Ask genuinely probing questions, not leading ones. Resist solving—help them see clearly first.

**Process:**
- Ask 1-3 focused questions per response
- Reflect back what you heard to confirm understanding
- Surface hidden assumptions and unstated constraints
- Don't provide solutions unless explicitly requested""",

    "plan": """Current Mode: Plan

You are an organizer. Structure and sequence work. Break large efforts into phases, identify dependencies, define next steps.

**Stance:** "How do we get this done?" Focus on actionable steps, order of operations, and deliverables. Make complexity manageable.

**Process:**
- Break work into discrete phases with clear outputs
- Identify dependencies and critical path
- Suggest immediate next steps (next 1-2 hours of work)
- Use numbered sequences and simple 2D diagrams""",

    "audit": """Current Mode: Audit

You are a pragmatic analyst. Evaluate against real-world constraints: cost, manufacturability, supply chain, regulatory, market fit.

**Stance:** "Will this work in the real world?" Be blunt about showstoppers. Quantify costs and risks with stated assumptions.

**Process:**
- Estimate costs with ranges and explicit assumptions
- Flag manufacturing constraints early (tolerances, processes, materials)
- Identify regulatory and compliance requirements
- Assess competitive landscape and market fit when relevant"""
}

MODE_ALERTS = {
    "balanced": "Switched to **Balanced** mode. Drawing on any mode's approach to help with your immediate need.",
    "challenge": "Switched to **Challenge** mode. I'll stress-test your design—finding weaknesses to help it survive scrutiny.",
    "explore": "Switched to **Explore** mode. Surveying prior art, standards, and alternatives before you commit.",
    "ideate": "Switched to **Ideate** mode. Generating ideas freely—quantity and novelty over feasibility.",
    "clarify": "Switched to **Clarify** mode. Asking questions to help sharpen your thinking.",
    "plan": "Switched to **Plan** mode. Breaking work into phases with clear next steps.",
    "audit": "Switched to **Audit** mode. Evaluating against real-world constraints: cost, manufacturability, and market fit."
}

def get_system_prompt(mode: str) -> str:
    """Assemble complete system prompt for a mode"""
    mode_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["balanced"])
    return f"{SHARED_GUIDELINES}\n---\n{mode_prompt}"

def get_mode_alert(mode: str) -> str:
    """Get the notification message when switching modes"""
    return MODE_ALERTS.get(mode, MODE_ALERTS["balanced"])
```

### 4.2 Chat Router with Mode Support

Create `backend/app/routers/chat.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from uuid import UUID
import anthropic
import os

from ..models.base import get_db
from ..models.conversation import Conversation, Message
from ..auth.jwt import get_current_user
from ..config.prompts import get_system_prompt

router = APIRouter(prefix="/api/conversations", tags=["chat"])

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL_MAP = {
    "opus": "claude-opus-4-5-20251101",
    "sonnet": "claude-sonnet-4-5-20241022",
    "haiku": "claude-3-5-haiku-20241022"
}

class ChatRequest(BaseModel):
    content: str
    model: str = "sonnet"

@router.post("/{conversation_id}/chat")
async def chat(
    conversation_id: UUID,
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get conversation
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.content,
        mode_used=conversation.current_mode
    )
    db.add(user_message)

    # Update title from first user message
    if conversation.title == "New Conversation":
        conversation.title = request.content[:50] + ("..." if len(request.content) > 50 else "")

    await db.commit()

    # Build messages array with history
    messages = []
    for msg in sorted(conversation.messages, key=lambda x: x.created_at):
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.content})

    # Get system prompt for current mode
    system_prompt = get_system_prompt(conversation.current_mode)
    model = MODEL_MAP.get(request.model, MODEL_MAP["sonnet"])

    async def generate():
        full_response = ""

        try:
            with client.messages.stream(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield {"event": "message", "data": text}

            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
                mode_used=conversation.current_mode
            )
            db.add(assistant_message)
            await db.commit()

            yield {"event": "done", "data": ""}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(generate())
```

### 4.3 Frontend Mode Selector Component

Create `frontend/components/ModeSelector.tsx`:

```tsx
'use client';

import { useState } from 'react';

const MODES = [
  { id: 'balanced', name: 'Balanced', icon: '◉', description: 'Direct generalist' },
  { id: 'challenge', name: 'Challenge', icon: '🛡️', description: 'Skeptical stress-tester' },
  { id: 'explore', name: 'Explore', icon: '🗺️', description: 'Neutral researcher' },
  { id: 'ideate', name: 'Ideate', icon: '💡', description: 'Creative generator' },
  { id: 'clarify', name: 'Clarify', icon: '❓', description: 'Socratic questioner' },
  { id: 'plan', name: 'Plan', icon: '☑️', description: 'Pragmatic sequencer' },
  { id: 'audit', name: 'Audit', icon: '💲', description: 'Feasibility analyst' },
];

interface ModeSelectorProps {
  currentMode: string;
  onModeChange: (mode: string) => void;
}

export default function ModeSelector({ currentMode, onModeChange }: ModeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const current = MODES.find(m => m.id === currentMode) || MODES[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500 rounded-lg text-amber-500 text-sm font-semibold"
      >
        <span>{current.icon}</span>
        <span>{current.name}</span>
        <span className="text-xs">▼</span>
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50">
          {MODES.map(mode => (
            <button
              key={mode.id}
              onClick={() => {
                onModeChange(mode.id);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 text-left text-sm hover:bg-gray-700 ${
                mode.id === currentMode ? 'bg-amber-500/20 text-amber-500' : 'text-gray-300'
              }`}
            >
              <span>{mode.icon}</span>
              <span>{mode.name}</span>
              {mode.id === currentMode && <span className="ml-auto">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Phase 4 Complete When:
- [ ] System prompts stored in config file
- [ ] Chat endpoint uses mode-specific system prompt
- [ ] Mode selector UI matches existing design
- [ ] Mode changes persist on conversation
- [ ] Different modes produce noticeably different AI responses

---

## Phase 5: Model Selection

**Goal:** Switch between Claude Opus/Sonnet/Haiku with cost indicators

### 5.1 Frontend Model Selector

Create `frontend/components/ModelSelector.tsx`:

```tsx
'use client';

import { useState } from 'react';

const MODELS = [
  { id: 'opus', name: 'Claude Opus 4.5', cost: '$$$', iconSize: 'text-xl' },
  { id: 'sonnet', name: 'Claude Sonnet 4.5', cost: '$$', iconSize: 'text-base' },
  { id: 'haiku', name: 'Claude Haiku 3.5', cost: '$', iconSize: 'text-sm' },
];

interface ModelSelectorProps {
  currentModel: string;
  onModelChange: (model: string) => void;
}

export default function ModelSelector({ currentModel, onModelChange }: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const current = MODELS.find(m => m.id === currentModel) || MODELS[1];

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3"
      >
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wide">Model</div>
          <div className="flex items-center gap-2 text-sm">
            <span className={`${current.iconSize}`}>🧠</span>
            <span>{current.name}</span>
          </div>
        </div>
        <span className="text-gray-500">▼</span>
      </button>

      {isOpen && (
        <div className="border-t border-gray-700 p-2">
          {MODELS.map(model => (
            <button
              key={model.id}
              onClick={() => {
                onModelChange(model.id);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded text-sm ${
                model.id === currentModel ? 'bg-teal-500/20 text-teal-400' : 'text-gray-400 hover:bg-gray-700'
              }`}
            >
              <span className={model.iconSize}>🧠</span>
              <span>{model.name}</span>
              <span className="ml-auto text-gray-500">{model.cost}</span>
              {model.id === currentModel && <span>✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 5.2 Haiku Drawing Warning

Add to chat component:

```tsx
const [haikuWarningShown, setHaikuWarningShown] = useState(false);

const checkHaikuDrawingWarning = (message: string) => {
  if (currentModel !== 'haiku' || haikuWarningShown) return;

  const drawingKeywords = ['draw', 'diagram', 'sketch', 'render', 'visualize', '2d', '3d'];
  const hasDrawingRequest = drawingKeywords.some(kw => message.toLowerCase().includes(kw));

  if (hasDrawingRequest) {
    showToast('Using Claude Haiku for drawings. For better results, consider Sonnet or Opus.', 'info');
    setHaikuWarningShown(true);
  }
};
```

### Phase 5 Complete When:
- [ ] Model selector in sidebar
- [ ] Selected model passed to chat endpoint
- [ ] Cost indicators display correctly
- [ ] Haiku warning shows once when requesting drawings

---

## Phase 6: File Upload

**Goal:** Upload files, attach to messages, persist in filesystem

### 6.1 Backend File Router

Create `backend/app/routers/files.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
import os
import shutil

from ..models.base import get_db
from ..auth.jwt import get_current_user

router = APIRouter(prefix="/api/files", tags=["files"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 10)) * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileResponse(BaseModel):
    id: str
    name: str
    type: str
    size: int
    url: str
    created_at: datetime

# In-memory file store (replace with DB in production)
file_store: dict = {}

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

    # Generate unique filename
    file_id = str(uuid4())
    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, user_id, stored_name)

    # Ensure user directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Store metadata
    file_data = {
        "id": file_id,
        "name": file.filename,
        "type": file.content_type or "application/octet-stream",
        "size": len(content),
        "path": file_path,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }
    file_store[file_id] = file_data

    return FileResponse(
        id=file_id,
        name=file.filename,
        type=file_data["type"],
        size=file_data["size"],
        url=f"/api/files/{file_id}",
        created_at=file_data["created_at"]
    )

@router.get("", response_model=List[FileResponse])
async def list_files(user_id: str = Depends(get_current_user)):
    user_files = [f for f in file_store.values() if f["user_id"] == user_id]
    return [
        FileResponse(
            id=f["id"],
            name=f["name"],
            type=f["type"],
            size=f["size"],
            url=f"/api/files/{f['id']}",
            created_at=f["created_at"]
        )
        for f in sorted(user_files, key=lambda x: x["created_at"], reverse=True)
    ]

@router.get("/{file_id}")
async def get_file(file_id: str, user_id: str = Depends(get_current_user)):
    file_data = file_store.get(file_id)
    if not file_data or file_data["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="File not found")

    from fastapi.responses import FileResponse as FastAPIFileResponse
    return FastAPIFileResponse(
        file_data["path"],
        filename=file_data["name"],
        media_type=file_data["type"]
    )
```

### 6.2 Frontend Upload Components

Create `frontend/components/FileUpload.tsx`:

```tsx
'use client';

import { useCallback, useState } from 'react';

interface FileUploadProps {
  onUpload: (files: File[]) => void;
}

export default function FileUpload({ onUpload }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    onUpload(files);
  }, [onUpload]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      onUpload(Array.from(e.target.files));
    }
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
        isDragging ? 'border-teal-500 bg-teal-500/10' : 'border-gray-600'
      }`}
    >
      <input
        type="file"
        multiple
        onChange={handleFileSelect}
        className="hidden"
        id="file-input"
      />
      <label htmlFor="file-input" className="cursor-pointer">
        <div className="w-12 h-12 mx-auto mb-3 bg-amber-500 rounded-full flex items-center justify-center">
          📁
        </div>
        <p className="font-semibold">Upload Files</p>
        <p className="text-sm text-gray-400">Drag & drop or click to browse</p>
      </label>
    </div>
  );
}
```

### Phase 6 Complete When:
- [ ] Files upload via drag & drop or click
- [ ] Upload progress indicator displays
- [ ] Files list in sidebar
- [ ] Files persist across page refresh
- [ ] Files can be attached to chat messages
- [ ] 10MB file size limit enforced

---

## Phase 7: Technical Drawings

**Goal:** 2D (Rough.js) and 3D (Three.js) drawings render in chat messages

### 7.1 Port TechDrawing Module

This is the largest single migration task. Port from existing `index.html`:
- `TechDrawing` object (~800 lines)
- `drawing-2d` and `drawing-3d` code block parsing
- Rough.js integration for sketchy style
- Three.js scene management
- SVG download functionality
- Fullscreen modal

Create `frontend/lib/techDrawing.ts` and `frontend/components/drawings/` directory.

### 7.2 Key Components to Create

```
frontend/components/drawings/
├── Drawing2D.tsx         # Rough.js SVG renderer
├── Drawing3D.tsx         # Three.js canvas
├── DrawingContainer.tsx  # Header, actions, fullscreen
└── drawingParser.ts      # Parse ```drawing-2d blocks
```

### 7.3 Dependencies

```bash
npm install roughjs three @types/three
```

### 7.4 Integration with Markdown

Process message content before rendering:

```tsx
import { parseDrawings, processContent } from '@/lib/techDrawing';

function MessageBody({ content }: { content: string }) {
  const processedContent = processContent(content);

  return (
    <div
      className="message-body"
      dangerouslySetInnerHTML={{ __html: marked.parse(processedContent) }}
    />
  );
}
```

### Phase 7 Complete When:
- [ ] `drawing-2d` blocks render as SVG
- [ ] Sketchy style uses Rough.js
- [ ] Technical style shows grid + title block
- [ ] Dimensions render with T-terminators
- [ ] `drawing-3d` blocks render with Three.js
- [ ] 3D drag to rotate, scroll to zoom
- [ ] Preset view buttons work
- [ ] SVG download works
- [ ] Fullscreen modal works
- [ ] 3D scenes cleanup on chat switch (no memory leaks)

---

## Phase 8: UI Polish

**Goal:** Match brand guidelines, responsive layout, theme system

### 8.1 Color Palette (from Brand Guidelines)

```css
:root {
  --bg-primary: #0f1e2e;
  --bg-secondary: #162d4a;
  --bg-tertiary: #1a3654;
  --bg-elevated: #244060;
  --text-primary: #F1F5F8;
  --text-secondary: #8795A1;
  --text-muted: #6b7a8a;
  --accent-primary: #2BA8A3;      /* Teal */
  --accent-secondary: #D4A03E;    /* Amber */
  --border-color: #3D4852;
  --danger: #ff4757;
  --success: #2ed573;
}

.light {
  --bg-primary: #F1F5F8;
  --bg-secondary: #FFFFFF;
  --bg-tertiary: #e8ecf2;
  /* ... inverted palette ... */
}
```

### 8.2 Tailwind Config

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'parallax': {
          'bg-primary': 'var(--bg-primary)',
          'bg-secondary': 'var(--bg-secondary)',
          // ...
        }
      }
    }
  }
}
```

### 8.3 Components to Style

- [ ] Sidebar (collapsible on mobile)
- [ ] Chat header with mode selector
- [ ] Message bubbles (user gradient, assistant solid)
- [ ] Input area with attachment preview
- [ ] Toast notifications
- [ ] Modals (confirmation, fullscreen)
- [ ] Loading/typing indicators

### Phase 8 Complete When:
- [ ] Dark/light theme toggle works
- [ ] Font size (small/medium/large) persists
- [ ] Mobile sidebar collapses properly
- [ ] All components match brand colors
- [ ] 44px minimum tap targets on mobile

---

## Phase 9: Search & Export

### 9.1 Backend Search Endpoint

```python
from sqlalchemy import or_

@router.get("/api/search")
async def search(
    q: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Search conversation titles and message content
    results = await db.execute(
        select(Conversation)
        .join(Message)
        .where(
            Conversation.user_id == user_id,
            or_(
                Conversation.title.ilike(f"%{q}%"),
                Message.content.ilike(f"%{q}%")
            )
        )
        .distinct()
    )
    return results.scalars().all()
```

### 9.2 PDF Export (Frontend)

Port `PDFExport` from existing code using jsPDF.

```bash
npm install jspdf
```

### Phase 9 Complete When:
- [ ] Global search modal (Cmd+K)
- [ ] Searches conversation titles and message content
- [ ] Search results clickable to load chat
- [ ] PDF export downloads correctly
- [ ] PDF includes metadata, cleans markdown

---

## Phase 10: Help System

### 10.1 Welcome Block

Show when conversation has no messages:
- Logo and tagline
- Feature list
- Mode reference table

### 10.2 Help Block

Inject into chat on help button click:
- Same content as welcome
- Dismissible

Port `getSharedHelpContentHTML()` from existing code.

### Phase 10 Complete When:
- [ ] Welcome block displays in empty chat
- [ ] Help button injects help block
- [ ] Help block dismissible
- [ ] Mode reference table displays correctly

---

## Phase 11: Production Deployment

### 11.1 Dockerfiles

**Backend Dockerfile (production):**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile (production):**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "server.js"]
```

### 11.2 Coolify Deployment Steps

1. Provision Hetzner CPX21 (3 vCPU, 4GB RAM, ~€8/mo)
2. Install Coolify via script
3. Configure domain DNS
4. Deploy services:
   - PostgreSQL (from Coolify templates)
   - Backend (Docker, from repo)
   - Frontend (Docker, from repo)
5. Configure environment variables in Coolify
6. Enable SSL via Coolify

### 11.3 Production Checklist

```
□ Environment variables set in Coolify
□ Database migrations run
□ CORS configured for production domain
□ JWT secret is secure (256-bit random)
□ HTTPS enforced
□ Database backups configured
□ Error monitoring (optional: Sentry)
```

### Phase 11 Complete When:
- [ ] All services deployed to VPS
- [ ] Domain resolves with SSL
- [ ] Can register, login, chat end-to-end
- [ ] File uploads work
- [ ] Technical drawings render

---

## Reference: Feature Inventory

### Core Chat System
- [ ] Conversation management (create, load, delete)
- [ ] Message persistence (PostgreSQL)
- [ ] Streaming responses (SSE)
- [ ] Auto-titling from first message

### Mode System (7 Modes)
| Mode | Icon | Status |
|------|------|--------|
| Balanced | ◉ | □ |
| Challenge | 🛡️ | □ |
| Explore | 🗺️ | □ |
| Ideate | 💡 | □ |
| Clarify | ❓ | □ |
| Plan | ☑️ | □ |
| Audit | 💲 | □ |

### Model Selection
- [ ] Claude Opus 4.5 ($$$)
- [ ] Claude Sonnet 4.5 ($$)
- [ ] Claude Haiku 3.5 ($)
- [ ] Haiku drawing warning

### File System
- [ ] Upload via click
- [ ] Upload via drag & drop
- [ ] Progress indicator
- [ ] 10MB limit
- [ ] Files sidebar

### Technical Drawings
- [ ] 2D parsing (`drawing-2d`)
- [ ] Sketchy style (Rough.js)
- [ ] Technical style (grid, title block)
- [ ] Dimensions (T-terminators)
- [ ] 3D parsing (`drawing-3d`)
- [ ] Three.js renderer
- [ ] View controls
- [ ] SVG download
- [ ] Fullscreen modal

### UI Features
- [ ] Dark/light theme
- [ ] Font size control
- [ ] Responsive sidebar
- [ ] Toast notifications
- [ ] Confirmation modals
- [ ] Typing indicator

### Search & Export
- [ ] Global search (Cmd+K)
- [ ] Sidebar search
- [ ] PDF export

### Help System
- [ ] Welcome block
- [ ] Help block (injected)

---

## Reference: System Prompts

See `backend/app/config/prompts.py` for complete prompts.

Each mode prompt follows the pattern:
1. Shared guidelines (always applied)
2. Mode-specific stance and process

---

## Reference: Brand Guidelines

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Primary | #1E3A5F | Headers, buttons |
| Secondary | #2B7A78 | Links, mode indicators |
| Accent | #D4A03E | CTAs, highlights |

### Typography
- Font: Inter (UI), JetBrains Mono (code)
- Hierarchy: Clear size/weight distinction

### Design Principles
- Clean & Functional
- Depth Through Subtlety
- Monochrome Icons
- Generous Whitespace

---

## Estimated Timeline

| Phase | Hours | Cumulative |
|-------|-------|------------|
| 0. Infrastructure | 2-3 | 3 |
| 1. Round Trip | 3-4 | 7 |
| 2. Auth | 4-6 | 13 |
| 3. Conversations | 4-5 | 18 |
| 4. Modes | 3-4 | 22 |
| 5. Models | 1-2 | 24 |
| 6. Files | 4-6 | 30 |
| 7. Drawings | 6-8 | 38 |
| 8. UI Polish | 4-6 | 44 |
| 9. Search/Export | 3-4 | 48 |
| 10. Help | 1-2 | 50 |
| 11. Deploy | 3-4 | 54 |

**Total: ~50-60 hours** (AI-assisted development)

---

## How to Use This Document with Claude Code

1. **Start each phase explicitly:**
   > "Complete Phase 0: Infrastructure Setup"

2. **Verify before proceeding:**
   > "Run the verification checklist for Phase 0"

3. **Move to next phase:**
   > "Phase 0 verified. Complete Phase 1: Minimal Round Trip"

4. **Reference sections as needed:**
   > "Show me the code for the Mode Selector from Phase 4"

5. **Check progress:**
   > "What features from the Feature Inventory are complete?"
