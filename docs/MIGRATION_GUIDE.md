# Parallax AI Migration Guide

**Poe Canvas App → FastAPI + Next.js + PostgreSQL**

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2025-01-02 | Initial migration plan |
| 2.0 | 2025-01-03 | Business plan integration |
| 3.0 | 2026-01-03 | Phase 4 complete, Phase 5 (Basic UI) added |

---

## Changelog (v3.0)

- **Phase 4**: Testing Infrastructure (formerly 3.1) - COMPLETE ✓
- **Phase 5 (NEW)**: Basic UI with shadcn/ui - Insert before Mode System
- **Phase 6+**: All subsequent phases renumbered
- **shadcn/ui adopted**: Modern component library for professional UI

## Changelog (v2.0)

- **Phase 2 expanded**: Usage tracking tables added to DB schema
- **Phase 5 (OLD)**: Domain System placeholder (OPTIONAL for v1) - now Phase 7
- **Phase 8 (OLD)**: Admin Dashboard (moved earlier for dev testing) - now Phase 10
- **Phase 9.5 (OLD)**: Usage Tracking & Tier Enforcement - now Phase 11.5
- **Phase 13 (OLD)**: Terms of Service - now Phase 15
- **Deferred**: Rate limiting (preference: 5 req/min when implemented)
- **Renumbered**: Phases shifted to accommodate new phases

---

## Phase Summary

| Phase | Name | Status | Change |
|-------|------|--------|--------|
| 0 | Infrastructure Setup | ✓ Complete | — |
| 1 | Minimal Round Trip | ✓ Complete | — |
| 2 | Database & Auth | ✓ Complete | EXPANDED |
| 3 | Conversation CRUD | ✓ Complete | — |
| 4 | Testing Infrastructure | ✓ Complete | NEW (v3.0) |
| **5** | **Basic UI (shadcn/ui)** | **In Progress** | **NEW (v3.0)** |
| 6 | Mode System | Pending | Renumbered |
| 7 | Domain System | Pending | NEW (Optional) |
| 8 | Model Selection | Pending | Renumbered |
| 9 | File Upload | Pending | Renumbered |
| 10 | Admin Dashboard | Pending | NEW (moved earlier) |
| 11 | Technical Drawings | Pending | Renumbered |
| 11.5 | Usage & Tier Enforcement | Pending | NEW |
| 12 | UI Polish | Pending | Renumbered |
| 13 | Search & Export | Pending | Renumbered |
| 14 | Help System | Pending | Renumbered |
| 15 | Terms of Service | Pending | NEW |
| 16 | Production Deployment | Pending | Renumbered |

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
│  • users, conversations, messages, usage_records    │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│            ANTHROPIC CLAUDE API                     │
│  • Claude Opus 4.5 / Sonnet 4.5 / Haiku 3.5        │
└─────────────────────────────────────────────────────┘
```

**Deployment Target:** Hetzner VPS + Coolify

---

## Phase 0: Infrastructure Setup ✓

**Status: COMPLETE**

Docker Compose, PostgreSQL, project structure, environment variables.

See v1.0 documentation for full details.

---

## Phase 1: Minimal Round Trip ✓

**Status: COMPLETE**

FastAPI skeleton, Next.js skeleton, SSE streaming from Claude API.

See v1.0 documentation for full details.

---

## Phase 2: Database & Auth (EXPANDED)

**Goal:** User registration, login, JWT-protected routes, usage tracking schema

### 2.1 User Model (Updated)

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    tier = Column(String(20), default="free")  # free, starter, builder, advanced
    tier_updated_at = Column(DateTime)  # For manual tier changes
    is_active = Column(Boolean, default=True)  # Kill switch
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Hash password using bcrypt"""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.password_hash)
```

**Dependencies required:**
```txt
passlib[bcrypt]==1.7.4
```

### 2.2 Usage Tracking Models (NEW)

```python
class UsageRecord(Base):
    """Individual usage events for detailed tracking"""
    __tablename__ = "usage_records"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    model = Column(String(50), nullable=False)  # haiku, sonnet, opus
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    conversation_id = Column(UUID, ForeignKey("conversations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class MonthlyUsage(Base):
    """Aggregated monthly usage for limit enforcement"""
    __tablename__ = "monthly_usage"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    month = Column(String(7), nullable=False)  # "2025-02"
    haiku_tokens = Column(Integer, default=0)
    sonnet_tokens = Column(Integer, default=0)
    opus_tokens = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'month', name='unique_user_month'),
    )
```

### 2.3 Tier Limits Config (NEW)

```python
# backend/app/config/tiers.py

from typing import Dict, TypedDict

class TierLimitDict(TypedDict):
    haiku: int
    sonnet: int
    opus: int

TIER_LIMITS: Dict[str, TierLimitDict] = {
    "free": {
        "haiku": 25_000,
        "sonnet": 0,
        "opus": 0,
    },
    "starter": {
        "haiku": 300_000,
        "sonnet": 0,
        "opus": 0,
    },
    "builder": {
        "haiku": 1_000_000,
        "sonnet": 200_000,
        "opus": 0,
    },
    "advanced": {
        "haiku": 2_000_000,
        "sonnet": 500_000,
        "opus": 100_000,
    },
}

def validate_tier(tier: str) -> bool:
    """Validate tier exists in config"""
    return tier in TIER_LIMITS

def get_tier_limits(tier: str) -> TierLimitDict:
    """Get limits with fallback to free tier"""
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])
```

### 2.4 Database Migrations (NEW)

Using Alembic for schema version control:

```bash
# Install Alembic
pip install alembic==1.13.1

# Initialize (one-time)
alembic init alembic

# Configure alembic.ini to use async DATABASE_URL
# Edit alembic/env.py to import models

# Create migration
alembic revision --autogenerate -m "Add users and usage tables"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Key files:**
- `alembic/env.py` - Configure async engine and import models
- `alembic/versions/` - Migration scripts
- `alembic.ini` - Database connection config

### 2.5 Required Dependencies (NEW)

Add to `backend/requirements.txt`:

```txt
# Database & ORM
sqlalchemy[asyncio]==2.0.23
alembic==1.13.1
asyncpg==0.29.0

# Auth & Security
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
```

### Phase 2 Verification

**Database:**
- [ ] Alembic configured with async engine
- [ ] Initial migration created and applied
- [ ] Tables exist: users, usage_records, monthly_usage
- [ ] Migration is reversible (downgrade works)

**Endpoints:**
- [ ] `POST /api/auth/register` creates user with hashed password
- [ ] `POST /api/auth/login` returns JWT token
- [ ] `GET /api/auth/me` returns current user (requires JWT)
- [ ] Invalid credentials return 401
- [ ] Duplicate email returns 400

**Models:**
- [ ] User model includes tier, is_active, password methods
- [ ] Tier limits config file exists with validation functions
- [ ] Password hashing works (bcrypt)
- [ ] JWT generation and validation works

**Tests:**
- [ ] Unit tests for user registration (valid/invalid email, password validation)
- [ ] Unit tests for login (correct/incorrect credentials)
- [ ] Unit tests for JWT token generation and validation
- [ ] Unit tests for protected endpoints (valid/invalid/expired tokens)
- [ ] Unit tests for tier validation functions
- [ ] **Test coverage ≥ 65%** for auth code
- [ ] **All auth tests pass:** `inv test.unit`

---

## Phase 3: Conversation CRUD

**Goal:** Create, list, load, delete conversations with message persistence

No changes from v1.0. See original documentation.

### Phase 3 Verification

- [X] `GET /api/conversations` returns user's conversations
- [X] `POST /api/conversations` creates new conversation
- [X] `GET /api/conversations/{id}` returns conversation with messages
- [X] `DELETE /api/conversations/{id}` removes conversation
- [X] `PATCH /api/conversations/{id}/mode` updates mode
- [X] All endpoints require valid JWT
- [X] Users can only access their own conversations

---

## Phase 4: Testing Infrastructure ✓

**Status: COMPLETE** (2026-01-03)

**Goal:** Implement modern testing infrastructure with real PostgreSQL and pytest-anyio

> ✅ **Completed:** 72% test coverage, 13 passing tests, real PostgreSQL integration

### 4.1 Dependencies

Add to `backend/requirements-dev.txt`:

```txt
# Testing Infrastructure
testcontainers>=4.8.2
pytest-anyio  # FastAPI 2025 standard (replaces pytest-asyncio for new tests)
asgi-lifespan  # For lifespan event testing
```

### 4.2 Migration from pytest-asyncio to pytest-anyio

**Why:** FastAPI official docs now recommend pytest-anyio for async testing (2025 standard).

**Benefits:**
- 4.2x performance improvement
- Better event loop management
- Simpler API
- Official FastAPI support

**Migration Steps:**

1. Update pytest.ini:
```ini
[pytest]
# Remove asyncio_mode if present
# asyncio_mode = auto  # DELETE THIS

# Keep existing markers and other config
markers =
    unit: Unit tests
    integration: Integration tests
    acceptance: Acceptance tests
```

2. Add anyio fixture to `tests/conftest.py`:
```python
import pytest

@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async backend for AnyIO."""
    return "asyncio"
```

3. Update test markers:
```python
# Old (pytest-asyncio)
@pytest.mark.asyncio
async def test_something():
    pass

# New (pytest-anyio)
@pytest.mark.anyio
async def test_something():
    pass
```

**Note:** Both can coexist during migration. Existing `@pytest.mark.asyncio` tests will continue to work.

### 4.3 Real PostgreSQL Integration (No Testcontainers)

Create `backend/tests/integration/conftest.py`:

```python
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.base import Base

@pytest.fixture(scope="session")
def postgres_container():
    """Provide PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="session")
async def test_engine(postgres_container):
    """Create async engine for test database."""
    # Convert psycopg2 URL to asyncpg
    database_url = postgres_container.get_connection_url().replace(
        "psycopg2", "asyncpg"
    )

    engine = create_async_engine(database_url, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    """Provide transactional database session for each test."""
    async_session = async_sessionmaker(
        test_engine,
        expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            # Rollback after each test for isolation
            await session.rollback()

@pytest.fixture
async def client(db_session):
    """Provide HTTP client with database override."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.dependencies import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

### 4.4 Enable Integration Tests

Update `backend/tests/integration/test_conversation_lifecycle.py`:

1. Remove the global `pytestmark` skip
2. Change `@pytest.mark.asyncio` to `@pytest.mark.anyio`
3. Tests should now run with real PostgreSQL via testcontainers

### Phase 4 Verification

- [X] pytest-anyio configured
- [X] Real PostgreSQL integration (docker-compose, not testcontainers)
- [X] PostgreSQL test database fixtures working (parallax_ai_test)
- [X] Integration tests pass with real PostgreSQL (3 tests)
- [X] Test isolation verified (transaction rollback)
- [X] Test coverage ≥ 65% (achieved 72%)
- [X] All unit tests passing (13 total)
- [X] Invoke tasks for test automation
- [X] bcrypt 4.2.1 pinned for passlib compatibility

### Phase 4 Notes

**Time Investment:** ~2-3 hours for full setup and debugging

**Benefits:**
- High-fidelity testing with real PostgreSQL
- No UUID/SQLite compatibility issues
- Better CI/CD integration
- Modern testing patterns (2025 standard)

**Can Skip If:**
- Under time pressure for v1 launch
- Manual testing + production monitoring acceptable
- Plan to add comprehensive testing post-launch

---

## Phase 5: Basic UI with shadcn/ui

**Status:** In Progress (2026-01-03)

**Goal:** Build functional UI with shadcn/ui components - professional look out of the box, emulate Poe Canvas layout

### 5.1 Why shadcn/ui?

**The Clear Choice for 2026:**
- ✅ **Industry standard** - De-facto choice for Next.js + Tailwind projects
- ✅ **Convention over configuration** - Sensible defaults, works out of the box
- ✅ **Looks great immediately** - Beautiful components without customization
- ✅ **Latest tech** - Built for Next.js 15, React 19, Tailwind CSS 4
- ✅ **Copy-paste approach** - You own the code, no runtime dependency
- ✅ **Built on Radix UI** - Rock-solid accessibility primitives

### 5.2 Setup

```bash
cd frontend

# Initialize shadcn/ui (interactive CLI)
npx shadcn@latest init

# Install required components
npx shadcn@latest add button input textarea select card avatar scroll-area separator dropdown-menu
```

**Note for React 19:** The shadcn CLI now handles `--legacy-peer-deps` automatically if needed.

### 5.3 Components to Build

**Authentication Pages:**
- Login page with Card/Input/Button components
- Register page with Card/Input/Button components
- Auth helpers (login, logout, getToken, isAuthenticated)

**Chat Layout:**
- Header with user info and logout
- Sidebar with ScrollArea and conversation list
- New Conversation button
- Main content area

**Chat Interface (Poe Canvas-inspired):**
- Centered message thread (max-w-3xl)
- Message bubbles with Avatar/Card components
- Mode selector (Select component)
- Model selector (Select component)
- Fixed message input (Textarea/Button)

**Icons:**
- Lucide React icons (Send, Plus, Trash2, LogOut, User, Bot)

### 5.4 Layout Reference (Poe Canvas Emulation)

```
┌───────────────────────────────────────────────┐
│  Header: [Mode ▼] [Model ▼] [User] [Logout] │
├───────────────────────────────────────────────┤
│                                                │
│  Message Thread (centered, max-width)         │
│                                                │
│  ┌──────────────────────────────────────────┐│
│  │ [U] User message                         ││
│  └──────────────────────────────────────────┘│
│                                                │
│  ┌──────────────────────────────────────────┐│
│  │ [A] Assistant response                   ││
│  └──────────────────────────────────────────┘│
│                                                │
├───────────────────────────────────────────────┤
│  [Type your message...              ] [Send] │
└───────────────────────────────────────────────┘
```

### 5.5 Files to Create

```
frontend/
├── components/ui/          # shadcn/ui components (9 files)
├── lib/
│   ├── utils.ts           # shadcn/ui utilities
│   ├── auth.ts            # Auth helpers
│   └── api.ts             # API client
├── types/
│   └── index.ts           # TypeScript types
└── app/
    ├── login/page.tsx
    ├── register/page.tsx
    └── chat/
        ├── layout.tsx
        ├── components/Sidebar.tsx
        └── [id]/
            ├── page.tsx
            └── components/
                ├── MessageList.tsx
                └── MessageInput.tsx
```

**Total:** ~21 new files

### 5.6 Known Limitations (Deferred to Phase 12 - UI Polish)

Phase 5 focuses on functionality with good-looking defaults. The following are intentionally deferred:

- ❌ Custom colors/brand theming
- ❌ Markdown rendering (plain text for now)
- ❌ Mobile responsive breakpoints
- ❌ Dark mode toggle
- ❌ Loading states/skeletons
- ❌ Custom hover/focus states
- ❌ Code syntax highlighting
- ❌ Message left/right alignment
- ❌ AI response persistence (deferred to Phase 6)

### Phase 5 Verification

- [X] shadcn/ui installed and configured
- [X] Login/register pages functional with shadcn/ui components
- [X] Chat layout with sidebar working
- [X] Messages display in centered, Poe-like layout
- [X] Message bubbles use Card/Avatar components
- [ ] Mode/Model selectors use Select components
- [X] Message input uses Textarea/Button
- [ ] Lucide icons throughout
- [X] Interface looks professional (shadcn/ui defaults)
- [X] Full user flow works: register → login → create conversation → chat → logout

**Estimated time:** ~9.5 hours

**Full plan:** See `docs/PHASE_5_PLAN_V2.md`

---

## Phase 5.1: Basic AI Chat (Haiku Model)

**Status:** ✅ Complete (2026-01-03)

**Goal:** Implement actual AI responses using Claude Haiku model with streaming

**Completion Document:** [PHASE_5.1_COMPLETE.md](./PHASE_5.1_COMPLETE.md)

### 5.1.1 Backend Integration

The chat endpoint already exists (`POST /api/chat`) but we need to verify it works correctly:

```python
# backend/app/routers/chat.py

@router.post("/chat", response_class=StreamingResponse)
async def chat_stream(
    request: ChatRequest,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream chat responses from Claude API"""
    # Get conversation and messages
    # Build system prompt (use 'balanced' mode as default)
    # Stream from Anthropic API
    # Save assistant message to database
    pass
```

### 5.1.2 Frontend Streaming Implementation

Update `frontend/src/lib/api.ts` to use the existing `streamChat` function:

```typescript
export async function streamChat(
  message: string,
  mode: string,
  model: string,
  onChunk: (text: string) => void,
  onError?: (error: Error) => void
): Promise<void> {
  // Existing SSE implementation
}
```

### 5.1.3 Chat Page Integration

Update `frontend/src/app/chat/page.tsx`:
- Remove placeholder assistant message
- Call `streamChat` function
- Display streaming text in real-time
- Save complete assistant message to database after stream finishes

### 5.1.4 Default Configuration

**Model:** Haiku (fast, cost-effective for testing)
**Mode:** Balanced (default)
**Defer:** Mode/Model selection UI to later phase

### Phase 5.1 Verification

- [x] User message saves to database
- [x] Assistant response streams from Claude API
- [x] Streaming text displays in real-time
- [x] Complete assistant message saves to database
- [x] Conversation history loads correctly
- [x] Multiple back-and-forth messages work
- [x] Error handling works (API errors, network errors)
- [x] Unit tests pass (13/13 active tests)
- [x] Integration tests pass (3/3)
- [x] Test coverage ≥65% (74.24%)

**Actual time:** ~6 hours (including debugging and test fixes)

---

## Phase 6: Mode System

**Goal:** 7 modes with distinct system prompts affecting AI behavior

No changes from v1.0. See original documentation for full prompt definitions.

### Phase 6 Verification

- [ ] System prompts stored in config file
- [ ] Chat endpoint uses mode-specific system prompt
- [ ] Mode selector UI working (already built in Phase 5)
- [ ] Mode changes persist on conversation
- [ ] Different modes produce noticeably different AI responses

---

## Phase 7: Domain System (NEW — OPTIONAL for v1)

**Goal:** Enable multi-domain operation (Engineering, Business, Writing, etc.)

> ⚠️ **This phase is optional for initial launch.** Can ship with Engineering-only and add domains post-launch.

### 7.1 Open Questions

- **UX:** Separate Domain selector vs. combined Mode+Domain selector?
- **Prompt structure:** Domain-specific base + mode overlay? Or 7×N distinct prompts?
- **Audit mode:** How does it adapt per domain?
  - Engineering → manufacturability, tolerances
  - Business → ROI, market fit
  - Writing → audience fit, clarity
- **Default domain:** User preference? Last used? Always ask?
- **Domain count:** Start with 3? 5? User-definable?

### 7.2 Proposed Data Model

```python
# Conversation model addition
current_domain = Column(String(30), default="engineering")

# Potential domains (TBD)
DOMAINS = [
    "engineering",   # Current prompts
    "business",      # Strategy, planning, analysis
    "writing",       # Content, copywriting, editing
    "research",      # Academic, literature review
    "product",       # Product management, roadmaps
]
```

### 7.3 Prototyping Tasks

- [ ] Sketch 2-3 UX options for domain selection
- [ ] Draft Business domain base prompt
- [ ] Draft Writing domain base prompt
- [ ] Test: Does mode behavior feel distinct across domains?
- [ ] Decision: Implement for v1 or defer?

### Phase 7 Verification

**Phase complete when:** Clear decision documented on whether to implement for launch or defer. If implementing, UX and prompt structure finalized.

---

## Phase 8: Model Selection

**Goal:** Switch between Claude Opus/Sonnet/Haiku with cost indicators

No changes from v1.0.

### Phase 8 Verification

- [ ] Model selector working (already built in Phase 5)
- [ ] Selected model passed to chat endpoint
- [ ] Cost indicators display correctly ($, $$, $$$)
- [ ] Haiku warning shows once when requesting drawings

---

## Phase 9: File Upload

**Goal:** Upload files, attach to messages, persist in filesystem

No changes from v1.0.

### Phase 9 Verification

- [ ] Files upload via drag & drop or click
- [ ] Upload progress indicator displays
- [ ] Files list in sidebar
- [ ] Files persist across page refresh
- [ ] Files can be attached to chat messages
- [ ] 10MB file size limit enforced

---

## Phase 10: Admin Dashboard (NEW)

**Goal:** Basic admin UI for user management and tier assignment

> Moved earlier to enable testing tier enforcement during development.

### 10.1 Admin Routes (Protected)

**Recommended approach using FastAPI dependency:**

```python
# backend/app/dependencies.py

import os
from fastapi import HTTPException, Depends
from app.models.user import User

async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that ensures current user is admin"""
    ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "").split(",")
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user
```

```python
# backend/app/routers/admin.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_admin_user, get_db
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users with usage stats"""
    # admin is guaranteed to be admin user
    pass


@router.patch("/users/{user_id}/tier")
async def update_tier(
    user_id: UUID,
    request: TierUpdateRequest,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually set user tier"""
    pass


@router.patch("/users/{user_id}/active")
async def toggle_active(
    user_id: UUID,
    request: ActiveUpdateRequest,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Kill switch - enable/disable user"""
    pass


@router.get("/stats")
async def get_stats(
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Total users, usage this month, cost estimate"""
    pass
```

**Alternative: Decorator approach** (if preferred):
```python
from functools import wraps

def require_admin(func):
    @wraps(func)
    async def wrapper(*args, user_id: str = Depends(get_current_user), db = Depends(get_db), **kwargs):
        user = await get_user(user_id, db)
        ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "").split(",")
        if user.email not in ADMIN_EMAILS:
            raise HTTPException(403, "Admin access required")
        return await func(*args, user_id=user_id, db=db, **kwargs)
    return wrapper

# Usage: @require_admin before route handlers
```

> **Recommendation:** Use the dependency approach for better testability and consistency with FastAPI patterns.

### 10.2 Admin UI Features

- [ ] User list table (email, tier, usage, last active)
- [ ] Tier dropdown to change user tier
- [ ] Toggle switch for is_active (kill switch)
- [ ] Dashboard stats: total users, active users, tokens this month
- [ ] Cost estimate display

### 10.3 Cost Estimation Formula

```python
def estimate_cost(haiku_tokens: int, sonnet_tokens: int, opus_tokens: int) -> float:
    """Estimate API cost in USD"""
    # Approximate blended cost per 1M tokens
    COST_PER_MILLION = {
        "haiku": 1.0,    # ~$0.25 in + $1.25 out, blended
        "sonnet": 12.0,  # ~$3 in + $15 out, blended
        "opus": 60.0,    # ~$15 in + $75 out, blended
    }
    return (
        haiku_tokens * COST_PER_MILLION["haiku"] / 1_000_000 +
        sonnet_tokens * COST_PER_MILLION["sonnet"] / 1_000_000 +
        opus_tokens * COST_PER_MILLION["opus"] / 1_000_000
    )
```

### Phase 10 Verification

- [ ] Admin page only accessible to configured admin emails
- [ ] Can view all users and their usage
- [ ] Can change user tier via UI
- [ ] Can disable user via UI (kill switch)
- [ ] Dashboard shows accurate stats and cost estimate

---

## Phase 11: Technical Drawings

**Goal:** 2D (Rough.js) and 3D (Three.js) drawings render in chat messages

No changes from v1.0. This is the largest single migration task (~800 lines).

### Phase 11 Verification

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

## Phase 11.5: Usage Tracking & Tier Enforcement (NEW)

**Goal:** Enforce token caps per tier, track usage, block requests when limits exceeded

### 11.5.1 Usage Service

```python
# backend/app/services/usage.py

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from ..config.tiers import TIER_LIMITS
from ..models.user import User
from ..models.usage import MonthlyUsage


async def get_current_month() -> str:
    """Get current month string for usage tracking"""
    return datetime.utcnow().strftime("%Y-%m")


async def get_monthly_usage(user_id: str, db: AsyncSession) -> dict:
    """Get user's token usage for current month"""
    month = await get_current_month()
    result = await db.execute(
        select(MonthlyUsage).where(
            MonthlyUsage.user_id == user_id,
            MonthlyUsage.month == month
        )
    )
    usage = result.scalar_one_or_none()
    
    if not usage:
        return {"haiku": 0, "sonnet": 0, "opus": 0}
    
    return {
        "haiku": usage.haiku_tokens,
        "sonnet": usage.sonnet_tokens,
        "opus": usage.opus_tokens
    }


async def check_limit(user: User, model: str, db: AsyncSession) -> tuple[bool, str]:
    """
    Check if user can use model.
    
    Returns:
        (allowed, reason) - allowed is True if request should proceed
    """
    # Check kill switch first
    if not user.is_active:
        return False, "Account suspended"
    
    limits = TIER_LIMITS.get(user.tier, TIER_LIMITS["free"])
    
    # Check if model is available on tier
    if limits.get(model, 0) == 0:
        return False, f"{model.title()} not available on {user.tier} tier"
    
    # Check usage against limit
    usage = await get_monthly_usage(str(user.id), db)
    if usage[model] >= limits[model]:
        return False, f"Monthly {model} limit reached ({limits[model]:,} tokens)"
    
    return True, ""


async def record_usage(
    user_id: str, 
    model: str, 
    input_tokens: int,
    output_tokens: int,
    conversation_id: str,
    db: AsyncSession
) -> None:
    """Record token usage after completion"""
    month = await get_current_month()
    total_tokens = input_tokens + output_tokens
    
    # Upsert monthly usage
    stmt = insert(MonthlyUsage).values(
        user_id=user_id,
        month=month,
        haiku_tokens=total_tokens if model == "haiku" else 0,
        sonnet_tokens=total_tokens if model == "sonnet" else 0,
        opus_tokens=total_tokens if model == "opus" else 0,
    ).on_conflict_do_update(
        constraint='unique_user_month',
        set_={
            f"{model}_tokens": MonthlyUsage.__table__.c[f"{model}_tokens"] + total_tokens
        }
    )
    await db.execute(stmt)
    await db.commit()
```

### 11.5.2 Chat Endpoint Integration

**Approach 1: Separate endpoint for usage reporting** (RECOMMENDED)

```python
# In routers/chat.py

@router.post("/{conversation_id}/chat")
async def chat(
    conversation_id: UUID,
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check kill switch and tier limit BEFORE calling API
    allowed, reason = await check_limit(user, request.model, db)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)

    # Stream normally without trying to record usage in generator
    async def generate():
        try:
            with client.messages.stream(
                model=MODEL_MAP[request.model],
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield {"event": "message", "data": text}

                # Send usage data as final event for frontend to report
                final_msg = stream.get_final_message()
                yield {
                    "event": "usage",
                    "data": {
                        "input_tokens": final_msg.usage.input_tokens,
                        "output_tokens": final_msg.usage.output_tokens
                    }
                }

            yield {"event": "done", "data": ""}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(generate())


@router.post("/{conversation_id}/usage")
async def report_usage(
    conversation_id: UUID,
    usage_data: UsageReport,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Frontend calls this after stream completes with usage data"""
    await record_usage(
        user_id=str(user.id),
        model=usage_data.model,
        input_tokens=usage_data.input_tokens,
        output_tokens=usage_data.output_tokens,
        conversation_id=str(conversation_id),
        db=db
    )
    return {"status": "recorded"}
```

**Approach 2: Background task** (Alternative)

```python
from fastapi import BackgroundTasks

@router.post("/{conversation_id}/chat")
async def chat(
    conversation_id: UUID,
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check limits...

    usage_tracker = {"input": 0, "output": 0}

    async def generate():
        nonlocal usage_tracker
        try:
            with client.messages.stream(...) as stream:
                for text in stream.text_stream:
                    yield {"event": "message", "data": text}

                final_msg = stream.get_final_message()
                usage_tracker["input"] = final_msg.usage.input_tokens
                usage_tracker["output"] = final_msg.usage.output_tokens

            yield {"event": "done", "data": ""}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    # Schedule usage recording as background task
    background_tasks.add_task(
        record_usage_after_stream,
        usage_tracker, user.id, request.model, conversation_id
    )

    return EventSourceResponse(generate())

async def record_usage_after_stream(tracker, user_id, model, conv_id):
    """Background task - runs after response sent"""
    if tracker["input"] > 0:
        async with get_async_session() as db:
            await record_usage(...)
```

> **Recommendation:** Use Approach 1 (separate endpoint) for simplicity and clarity. Frontend calls `/usage` endpoint after stream completes.

### 11.5.3 Usage Display Endpoint

```python
@router.get("/api/usage")
async def get_usage(
    user_id: str = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Get current user's usage and limits"""
    user = await get_user(user_id, db)
    limits = TIER_LIMITS[user.tier]
    usage = await get_monthly_usage(user_id, db)
    
    return {
        "tier": user.tier,
        "limits": limits,
        "usage": usage,
        "remaining": {
            model: max(0, limits[model] - usage[model])
            for model in limits
        }
    }
```

### 11.5.4 Frontend Usage Display

Add usage bar to sidebar showing tokens remaining per model.

Color coding:
- Green: >50% remaining
- Yellow: 10-50% remaining  
- Red: <10% remaining

### Phase 11.5 Verification

- [ ] Free tier cannot access Sonnet or Opus (returns 429)
- [ ] Usage increments after each message
- [ ] Request blocked with 429 when limit reached
- [ ] Usage resets at month boundary
- [ ] Kill switch (is_active=False) blocks all requests
- [ ] Frontend displays usage remaining
- [ ] Usage endpoint returns accurate data

---

## Phase 12: UI Polish

**Goal:** Match brand guidelines, responsive layout, theme system

No changes from v1.0.

**Note:** Phase 5 (Basic UI) provides foundation. Phase 12 adds polish:
- Custom colors/brand theming
- Markdown rendering with react-markdown
- Code syntax highlighting
- Mobile responsive breakpoints
- Dark/light mode toggle
- Loading states/skeletons
- Custom hover/focus states
- Message left/right alignment

### Phase 12 Verification

- [ ] Dark/light theme toggle works
- [ ] Font size (small/medium/large) persists
- [ ] Mobile sidebar collapses properly
- [ ] All components match brand colors
- [ ] 44px minimum tap targets on mobile
- [ ] Markdown rendering works
- [ ] Code syntax highlighting works
- [ ] Loading states for all async operations

---

## Phase 13: Search & Export

**Goal:** Global search, PDF export

No changes from v1.0.

### Phase 13 Verification

- [ ] Global search modal (Cmd+K)
- [ ] Searches conversation titles and message content
- [ ] Search results clickable to load chat
- [ ] PDF export downloads correctly
- [ ] PDF includes metadata, cleans markdown

---

## Phase 14: Help System

**Goal:** Welcome block, help injection

No changes from v1.0.

### Phase 14 Verification

- [ ] Welcome block displays in empty chat
- [ ] Help button injects help block
- [ ] Help block dismissible
- [ ] Mode reference table displays correctly

---

## Phase 15: Terms of Service (NEW)

**Goal:** "Best effort" support language, liability limitations

### 15.1 Required Pages

- [ ] `/terms` - Terms of Service
- [ ] `/privacy` - Privacy Policy

### 15.2 Key Language Requirements

| Topic | Required Language |
|-------|-------------------|
| Support | "Best effort basis. No guaranteed response time." |
| Availability | "Service provided as-is. No uptime guarantees." |
| Data | "Conversations may be deleted. Export your data regularly." |
| Liability | "Maximum liability limited to fees paid in prior 12 months." |

### 15.3 Implementation

- [ ] Terms of Service page exists
- [ ] Privacy Policy page exists
- [ ] Registration requires ToS checkbox
- [ ] Footer links on all pages
- [ ] Last updated date displayed

### Phase 15 Verification

- [ ] Cannot register without accepting ToS
- [ ] Terms accessible from all pages
- [ ] Language covers support, availability, data, liability

---

## Phase 16: Production Deployment

**Goal:** Deploy to Hetzner VPS with Coolify

No changes from v1.0.

### Phase 16 Verification

- [ ] All services deployed to VPS
- [ ] Domain resolves with SSL
- [ ] Can register, login, chat end-to-end
- [ ] File uploads work
- [ ] Technical drawings render
- [ ] Admin dashboard accessible

---

## Deferred Features

Features explicitly deferred from initial launch:

### Rate Limiting

- **Preference when implemented:** 5 requests/minute
- **Implementation:** Redis + sliding window, or in-memory for MVP
- **Trigger to add:** If abuse detected or costs spike unexpectedly

### Payment Integration

- **Launch approach:** Manual tier assignment via admin dashboard
- **Future:** Stripe Checkout for self-serve upgrades
- **Trigger to add:** When manual tier changes become burdensome

### Abuse Detection

- **Launch approach:** Token caps + manual monitoring via admin dashboard
- **Future:** Automated alerts when usage patterns anomalous

---

## Timeline Estimate

| Phase | Hours | Cumulative |
|-------|-------|------------|
| 0. Infrastructure ✓ | 2-3 | 3 |
| 1. Round Trip ✓ | 3-4 | 7 |
| 2. Auth (expanded) ✓ | 5-7 | 14 |
| 3. Conversations ✓ | 4-5 | 19 |
| 4. Testing ✓ | 6-8 | 27 |
| **5. Basic UI (shadcn/ui)** | **9-10** | **37** |
| 6. Modes | 3-4 | 41 |
| 7. Domains (optional) | 0-4 | 45 |
| 8. Models | 1-2 | 47 |
| 9. Files | 4-6 | 53 |
| 10. Admin Dashboard | 4-6 | 59 |
| 11. Drawings | 6-8 | 67 |
| 11.5. Usage & Tiers | 4-6 | 73 |
| 12. UI Polish | 4-6 | 79 |
| 13. Search/Export | 3-4 | 83 |
| 14. Help | 1-2 | 85 |
| 15. ToS | 1-2 | 87 |
| 16. Deploy | 3-4 | 91 |

**Total: ~75-90 hours** (AI-assisted development)

**Current Progress: 27 hours complete (Phases 0-4 ✓)**

---

## Environment Variables Reference

```bash
# Backend - Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Backend - External APIs
ANTHROPIC_API_KEY=sk-ant-...

# Backend - Auth & Security
JWT_SECRET=your-256-bit-secret-here  # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_SALT_ROUNDS=12  # For bcrypt

# Backend - CORS
CORS_ORIGINS=https://your-domain.com,http://localhost:3000  # Comma-separated

# Backend - File Uploads
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10

# Backend - Admin
ADMIN_EMAILS=admin@example.com,admin2@example.com  # Comma-separated

# Frontend
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXTAUTH_SECRET=your-nextauth-secret  # Generate with: openssl rand -base64 32
NEXTAUTH_URL=https://your-domain.com
```

---

## How to Use This Document

1. **Start each phase explicitly:**
   > "Complete Phase 2: Database & Auth"

2. **Verify before proceeding:**
   > "Run the verification checklist for Phase 2"

3. **Move to next phase:**
   > "Phase 2 verified. Complete Phase 3: Conversation CRUD"

4. **Skip optional phases if needed:**
   > "Skip Phase 5 (Domain System) for now, proceed to Phase 6"

5. **Check progress:**
   > "Which phases are complete? What's next?"
---

## Ongoing Improvements & Future Enhancements

This section tracks improvements, features, and tasks that should be incorporated into the migration plan. **Review this section periodically** and integrate items into logical phases when appropriate.

### DevOps & Deployment

- [ ] **GitHub Actions CI/CD**
  - Set up automated testing on push/PR
  - Add deployment pipeline to staging environment
  - Consider: Hetzner Cloud staging instance or similar
  - Deployment target: Coolify on staging VPS
  - **Suggested Phase:** Add to Phase 14 (Production Deployment) or create new Phase 14.5

### Security Hardening

- [ ] **Frontend Security Fortification**
  - Protect against XSS (Cross-Site Scripting)
  - Implement CSP (Content Security Policy) headers
  - Add CSRF protection for forms
  - Secure cookie settings (httpOnly, secure, sameSite)
  - Input sanitization and validation
  - Rate limiting on sensitive endpoints
  - Consider: DOMPurify for user-generated content
  - **Suggested Phase:** Add to Phase 10 (UI Polish) or create Phase 10.5 (Security Hardening)

- [ ] **Backend Security Audit**
  - SQL injection prevention (verify SQLAlchemy usage)
  - Command injection prevention
  - Server-side input validation
  - Secure password reset flow
  - Session management review
  - API rate limiting implementation
  - **Suggested Phase:** Add to Phase 2 verification or Phase 10.5

### Database Management

- [ ] **PostgreSQL Admin Interface**
  - Research options:
    - **pgAdmin** (full-featured GUI)
    - **django-admin-honeypot** (if using Django)
    - **Flask-Admin** with SQLAlchemy (lightweight)
    - **Adminer** (single-file PHP, simple)
    - **DBeaver** (desktop client)
  - Requirements:
    - View table data
    - Access logs and query performance
    - User management
    - Backup/restore capabilities
  - Security considerations: IP whitelist, strong auth
  - **Suggested Phase:** Add to Phase 8 (Admin Dashboard) as separate admin DB tools section

### How to Use This Section

1. **Regular Review:** Check this section at the end of each phase
2. **Prioritize:** Discuss which items are critical vs. nice-to-have
3. **Integrate:** Move items into appropriate phases with:
   - Clear acceptance criteria
   - Testing requirements
   - Documentation updates
4. **Track Progress:** Mark items as complete when fully integrated into a phase
5. **Add New Items:** Append new improvement ideas as they arise

### Example Integration Workflow

```
1. Review "Ongoing Improvements" section
2. Identify item: "Frontend Security Fortification"
3. Decision: Critical for production launch
4. Action: Add to Phase 10 (UI Polish) as "10.6: Security Hardening"
5. Update Phase 10 with:
   - Security checklist
   - Testing requirements
   - Verification criteria
6. Mark item in this section as integrated
```

---

## Notes for AI Assistants

When helping with this project:

1. **Check this section regularly** - Don't let todos accumulate indefinitely
2. **Suggest integration points** - Recommend where items fit best in existing phases
3. **Ask about priorities** - Clarify with the user which improvements are most important
4. **Update both sections** - When integrating an item, update both the phase and this section
5. **Track phase status** - Update Phase Summary table as phases are completed

