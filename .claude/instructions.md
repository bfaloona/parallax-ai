# Parallax AI - Claude Code Instructions

## Project Overview

**Parallax AI** is a technical design assistant being migrated from a Poe Canvas app to a self-hosted FastAPI + Next.js application.

**Tech Stack:**
- Backend: FastAPI (Python 3.11+) + PostgreSQL 16 + SQLAlchemy 2.0
- Frontend: Next.js 14 (TypeScript, Tailwind CSS)
- LLM: Direct Anthropic Claude API (no Langflow)
- Deployment: Hetzner VPS + Coolify

---

## Core Concept: The 7-Mode System

The defining feature is a **7-mode system** providing distinct intellectual stances:

| Mode | Stance | Icon |
|------|--------|------|
| **Balanced** | Direct generalist | ◉ |
| **Challenge** | Skeptical stress-tester | 🛡️ |
| **Explore** | Neutral researcher | 🗺️ |
| **Ideate** | Creative generator | 💡 |
| **Clarify** | Socratic questioner | ❓ |
| **Plan** | Pragmatic sequencer | ☑️ |
| **Audit** | Feasibility analyst | 💲 |

Each mode has a unique system prompt stored in `backend/app/config/prompts.py`.

---

## Key Features

1. **Chat System**: Streaming responses (SSE), conversation persistence, message history
2. **Technical Drawings**: Parse `drawing-2d` (Rough.js) and `drawing-3d` (Three.js) code blocks
3. **File Upload**: Drag & drop, 10MB limit, user-specific storage
4. **Model Selection**: Opus/Sonnet/Haiku with cost indicators
5. **Search & Export**: Global search (Cmd+K), PDF export
6. **Responsive UI**: Dark/light theme, mobile-friendly, brand colors

---

## Code Style

### Backend (Python/FastAPI)
- Async/await throughout
- Type hints required
- Pydantic for validation
- SQLAlchemy 2.0 async patterns
- JWT auth via `Depends(get_current_user)`

### Frontend (TypeScript/Next.js)
- Strict TypeScript (avoid `any`)
- Client components: `'use client'`
- Tailwind CSS for styling
- API client in `lib/api.ts`

---

## Critical Implementation Notes

### Mode System
- **Never hardcode prompts** in handlers
- Import from `backend/app/config/prompts.py`
- Use `get_system_prompt(mode)` helper

### Technical Drawings
- ~800 lines to port from original Poe app
- Rough.js for sketchy 2D, Three.js for 3D
- **Must dispose Three.js scenes** to prevent memory leaks

### File Upload
- Validate MIME types
- Store: `/uploads/{user_id}/{file_id}.{ext}`
- Serve via `/api/files/{file_id}` (never expose paths)

### Security
- Verify user ownership before DB operations
- 256-bit JWT secret
- CORS limited to allowed origins
- HTTPS enforced in production

---

## Reference Documents

All detailed implementation steps, code examples, and architecture diagrams are in:

📄 **`docs/MIGRATION_GUIDE.md`**

The guide contains:
- 11 development phases with complete code
- Database schemas
- API endpoint specifications
- Component examples
- Brand guidelines
- Deployment instructions

---

## Working with This Project

### Starting Work
Refer to the Migration Guide for phase-by-phase implementation:
```
"Complete Phase N from the migration guide"
```

### When Making Changes
- Follow patterns established in Migration Guide
- Reference brand colors from guide
- Use database schema from guide
- Check verification checklists

### Common Commands
```
"Show me Phase 4 from the migration guide"
"What's the database schema for conversations?"
"What are the brand colors?"
```

---

## Development Workflow

1. **Read** `docs/MIGRATION_GUIDE.md` for implementation details
2. **Follow** code style conventions above
3. **Test** each component before moving forward
4. **Verify** user authentication and ownership
5. **Clean up** resources (especially Three.js scenes)

---

## Critical Development Guidelines

### Naming Conventions - Branch Directory Independence

**IMPORTANT**: Claude Code runs in temporary git worktrees with auto-generated names (e.g., `eager-pare`, `unruffled-shirley`). These names change between sessions.

**NEVER** hardcode branch directory names anywhere in the codebase:

❌ **Bad Examples:**
```python
container_name = "eager-pare-backend-1"  # Will break in next session
path = "/Users/user/.claude-worktrees/parallax-ai/eager-pare/uploads"
```

✅ **Good Examples:**
```python
# Use docker-compose service names
c.run("docker-compose exec backend /bin/sh")

# Use relative paths
upload_dir = "./uploads"  # or os.getenv("UPLOAD_DIR")

# Use dynamic container detection
c.run("docker ps --filter name=backend", hide=True)
```

**Why This Matters**: Hardcoded worktree names will fail when:
- Claude Code creates a new worktree in a different session
- Another developer clones the repo
- CI/CD runs in a different environment

**What to Do Instead**:
- Use `docker-compose exec` instead of `docker exec`
- Use environment variables for paths
- Use service names, not container names
- Make invoke tasks work regardless of worktree name
- Set explicit project name in docker-compose.yml (see Docker Compose Project Names below)

---

## Common Pitfalls (Phase 1 Learnings)

### Docker Compose Project Names

**CRITICAL**: Docker Compose uses the directory name as the default project name, which causes container names to include the worktree directory name.

**Problem**: Without an explicit project name, containers are named `{directory}-{service}-1`:
- In worktree `unruffled-shirley`: `unruffled-shirley-postgres-1`
- In worktree `eager-pare`: `eager-pare-postgres-1`
- This breaks consistency and makes container management difficult

**Solution**: Set an explicit project name in docker-compose.yml:
```yaml
version: '3.8'

name: parallax-ai  # ✓ Fixed project name

services:
  postgres:
    # ...
```

Now containers are always named:
- `parallax-ai-postgres-1`
- `parallax-ai-backend-1`
- `parallax-ai-frontend-1`

Regardless of worktree directory name.

### Docker Environment Variables

**CRITICAL**: When using docker-compose with both `env_file` and `environment`:

- Variables in `environment:` with `${VAR}` syntax get substituted from **shell environment**, NOT from .env file
- If shell variable is empty, it overrides env_file with empty string
- This causes silent failures that are hard to debug

**Example - DON'T DO THIS:**
```yaml
env_file: .env
environment:
  API_KEY: ${API_KEY}  # ❌ Overrides .env if $API_KEY not in shell
```

**Example - DO THIS:**
```yaml
env_file: .env
environment:
  CORS_ORIGINS: http://localhost:3000  # ✓ Literal values OK
  # API_KEY will come from .env file automatically
```

**Debug Command:**
```bash
docker-compose config | grep API_KEY  # Shows resolved value
```

### Python/FastAPI Dependencies

- Always check Python version compatibility (3.11 vs 3.13)
- Pin exact versions in requirements.txt to avoid conflicts
- Common conflicts: pydantic/httpx, anthropic/httpx
- Test `docker build` before `docker-compose up`

**Phase 1 Working Versions:**
```
fastapi==0.115.6
uvicorn[standard]==0.32.1
anthropic==0.42.0
pydantic==2.10.3
httpx==0.27.2  # Must be compatible with anthropic
```

### Anthropic API

- Model IDs change - always check current API docs
- Current models (Jan 2025): `claude-sonnet-4-20250514`, `claude-opus-4-5-20251101`
- Test with curl before integrating into app
- Watch for 404 errors indicating wrong model ID

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' \
  --max-time 10
```

---

## Success Criteria

Migration complete when:
- ✅ All 7 modes work with distinct behavior
- ✅ Technical drawings render (2D + 3D)
- ✅ File upload functional
- ✅ Search and export working
- ✅ Responsive UI matches brand
- ✅ Deployed to production with SSL

---

**Note**: This document provides high-level context. For implementation details, code examples, and step-by-step instructions, always reference `docs/MIGRATION_GUIDE.md`.
