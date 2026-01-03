# Parallax AI Migration Guide

**Poe Canvas App → FastAPI + Next.js + PostgreSQL**

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2025-01-02 | Initial migration plan |
| 2.0 | 2025-01-03 | Business plan integration |

---

## Changelog (v2.0)

- **Phase 2 expanded**: Usage tracking tables added to DB schema
- **Phase 5 (NEW)**: Domain System placeholder (OPTIONAL for v1)
- **Phase 8 (NEW)**: Admin Dashboard (moved earlier for dev testing)
- **Phase 9.5 (NEW)**: Usage Tracking & Tier Enforcement
- **Phase 13 (NEW)**: Terms of Service
- **Deferred**: Rate limiting (preference: 5 req/min when implemented)
- **Renumbered**: Phases shifted to accommodate new phases

---

## Phase Summary

| Phase | Name | Status | Change |
|-------|------|--------|--------|
| 0 | Infrastructure Setup | ✓ Complete | — |
| 1 | Minimal Round Trip | ✓ Complete | — |
| 2 | Database & Auth | ✓ Complete | EXPANDED |
| 3 | Conversation CRUD | Pending | — |
| 4 | Mode System | Pending | — |
| 5 | Domain System | Pending | NEW (Optional) |
| 6 | Model Selection | Pending | — |
| 7 | File Upload | Pending | — |
| 8 | Admin Dashboard | Pending | NEW (moved earlier) |
| 9 | Technical Drawings | Pending | Renumbered |
| 9.5 | Usage & Tier Enforcement | Pending | NEW |
| 10 | UI Polish | Pending | Renumbered |
| 11 | Search & Export | Pending | Renumbered |
| 12 | Help System | Pending | Renumbered |
| 13 | Terms of Service | Pending | NEW |
| 14 | Production Deployment | Pending | Renumbered |

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

No changes from v1.0. See original documentation for full prompt definitions.

### Phase 4 Verification

- [ ] System prompts stored in config file
- [ ] Chat endpoint uses mode-specific system prompt
- [ ] Mode selector UI matches design
- [ ] Mode changes persist on conversation
- [ ] Different modes produce noticeably different AI responses

---

## Phase 5: Domain System (NEW — OPTIONAL for v1)

**Goal:** Enable multi-domain operation (Engineering, Business, Writing, etc.)

> ⚠️ **This phase is optional for initial launch.** Can ship with Engineering-only and add domains post-launch.

### 5.1 Open Questions

- **UX:** Separate Domain selector vs. combined Mode+Domain selector?
- **Prompt structure:** Domain-specific base + mode overlay? Or 7×N distinct prompts?
- **Audit mode:** How does it adapt per domain?
  - Engineering → manufacturability, tolerances
  - Business → ROI, market fit
  - Writing → audience fit, clarity
- **Default domain:** User preference? Last used? Always ask?
- **Domain count:** Start with 3? 5? User-definable?

### 5.2 Proposed Data Model

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

### 5.3 Prototyping Tasks

- [ ] Sketch 2-3 UX options for domain selection
- [ ] Draft Business domain base prompt
- [ ] Draft Writing domain base prompt
- [ ] Test: Does mode behavior feel distinct across domains?
- [ ] Decision: Implement for v1 or defer?

### Phase 5 Verification

**Phase complete when:** Clear decision documented on whether to implement for launch or defer. If implementing, UX and prompt structure finalized.

---

## Phase 6: Model Selection

**Goal:** Switch between Claude Opus/Sonnet/Haiku with cost indicators

No changes from v1.0.

### Phase 6 Verification

- [ ] Model selector in sidebar
- [ ] Selected model passed to chat endpoint
- [ ] Cost indicators display correctly ($, $$, $$$)
- [ ] Haiku warning shows once when requesting drawings

---

## Phase 7: File Upload

**Goal:** Upload files, attach to messages, persist in filesystem

No changes from v1.0.

### Phase 7 Verification

- [ ] Files upload via drag & drop or click
- [ ] Upload progress indicator displays
- [ ] Files list in sidebar
- [ ] Files persist across page refresh
- [ ] Files can be attached to chat messages
- [ ] 10MB file size limit enforced

---

## Phase 8: Admin Dashboard (NEW)

**Goal:** Basic admin UI for user management and tier assignment

> Moved earlier to enable testing tier enforcement during development.

### 8.1 Admin Routes (Protected)

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

### 8.2 Admin UI Features

- [ ] User list table (email, tier, usage, last active)
- [ ] Tier dropdown to change user tier
- [ ] Toggle switch for is_active (kill switch)
- [ ] Dashboard stats: total users, active users, tokens this month
- [ ] Cost estimate display

### 8.3 Cost Estimation Formula

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

### Phase 8 Verification

- [ ] Admin page only accessible to configured admin emails
- [ ] Can view all users and their usage
- [ ] Can change user tier via UI
- [ ] Can disable user via UI (kill switch)
- [ ] Dashboard shows accurate stats and cost estimate

---

## Phase 9: Technical Drawings

**Goal:** 2D (Rough.js) and 3D (Three.js) drawings render in chat messages

No changes from v1.0. This is the largest single migration task (~800 lines).

### Phase 9 Verification

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

## Phase 9.5: Usage Tracking & Tier Enforcement (NEW)

**Goal:** Enforce token caps per tier, track usage, block requests when limits exceeded

### 9.5.1 Usage Service

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

### 9.5.2 Chat Endpoint Integration

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

### 9.5.3 Usage Display Endpoint

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

### 9.5.4 Frontend Usage Display

Add usage bar to sidebar showing tokens remaining per model.

Color coding:
- Green: >50% remaining
- Yellow: 10-50% remaining  
- Red: <10% remaining

### Phase 9.5 Verification

- [ ] Free tier cannot access Sonnet or Opus (returns 429)
- [ ] Usage increments after each message
- [ ] Request blocked with 429 when limit reached
- [ ] Usage resets at month boundary
- [ ] Kill switch (is_active=False) blocks all requests
- [ ] Frontend displays usage remaining
- [ ] Usage endpoint returns accurate data

---

## Phase 10: UI Polish

**Goal:** Match brand guidelines, responsive layout, theme system

No changes from v1.0.

### Phase 10 Verification

- [ ] Dark/light theme toggle works
- [ ] Font size (small/medium/large) persists
- [ ] Mobile sidebar collapses properly
- [ ] All components match brand colors
- [ ] 44px minimum tap targets on mobile

---

## Phase 11: Search & Export

**Goal:** Global search, PDF export

No changes from v1.0.

### Phase 11 Verification

- [ ] Global search modal (Cmd+K)
- [ ] Searches conversation titles and message content
- [ ] Search results clickable to load chat
- [ ] PDF export downloads correctly
- [ ] PDF includes metadata, cleans markdown

---

## Phase 12: Help System

**Goal:** Welcome block, help injection

No changes from v1.0.

### Phase 12 Verification

- [ ] Welcome block displays in empty chat
- [ ] Help button injects help block
- [ ] Help block dismissible
- [ ] Mode reference table displays correctly

---

## Phase 13: Terms of Service (NEW)

**Goal:** "Best effort" support language, liability limitations

### 13.1 Required Pages

- [ ] `/terms` - Terms of Service
- [ ] `/privacy` - Privacy Policy

### 13.2 Key Language Requirements

| Topic | Required Language |
|-------|-------------------|
| Support | "Best effort basis. No guaranteed response time." |
| Availability | "Service provided as-is. No uptime guarantees." |
| Data | "Conversations may be deleted. Export your data regularly." |
| Liability | "Maximum liability limited to fees paid in prior 12 months." |

### 13.3 Implementation

- [ ] Terms of Service page exists
- [ ] Privacy Policy page exists
- [ ] Registration requires ToS checkbox
- [ ] Footer links on all pages
- [ ] Last updated date displayed

### Phase 13 Verification

- [ ] Cannot register without accepting ToS
- [ ] Terms accessible from all pages
- [ ] Language covers support, availability, data, liability

---

## Phase 14: Production Deployment

**Goal:** Deploy to Hetzner VPS with Coolify

No changes from v1.0.

### Phase 14 Verification

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
| 2. Auth (expanded) | 5-7 | 14 |
| 3. Conversations | 4-5 | 19 |
| 4. Modes | 3-4 | 23 |
| 5. Domains (optional) | 0-4 | 27 |
| 6. Models | 1-2 | 29 |
| 7. Files | 4-6 | 35 |
| 8. Admin Dashboard | 4-6 | 41 |
| 9. Drawings | 6-8 | 49 |
| 9.5. Usage & Tiers | 4-6 | 55 |
| 10. UI Polish | 4-6 | 61 |
| 11. Search/Export | 3-4 | 65 |
| 12. Help | 1-2 | 67 |
| 13. ToS | 1-2 | 69 |
| 14. Deploy | 3-4 | 73 |

**Total: ~60-75 hours** (AI-assisted development)

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

