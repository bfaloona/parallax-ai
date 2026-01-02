# Phase 0: Infrastructure Setup - COMPLETE ✓

**Completed:** January 2, 2026
**Reference:** docs/MIGRATION_GUIDE.md (Phase 0: Infrastructure Setup)

---

## Summary

Phase 0 has been successfully completed. All infrastructure components are running and verified. The project has been migrated from a Langflow-based architecture to a direct Anthropic API integration.

---

## Verification Checklist

### Prerequisites ✓

- [x] Docker and Docker Compose installed
  - Docker version 29.1.3
  - Docker Compose version 5.0.1
- [x] Node.js 20+ installed
  - Node.js v24.10.0
- [x] Python 3.11+ installed
  - Python 3.13.3

### Configuration ✓

- [x] `.env.example` updated with Phase 0 requirements
  - POSTGRES_USER=parallax
  - POSTGRES_DB=parallax_ai
  - DATABASE_URL with postgresql+asyncpg driver
  - ANTHROPIC_API_KEY placeholder
  - JWT authentication configuration
  - File upload configuration
  - Removed all Langflow references

- [x] `.env` file configured (not committed to git)
  - Database credentials set
  - Placeholders for ANTHROPIC_API_KEY and JWT_SECRET

### Docker Infrastructure ✓

- [x] `docker-compose.yml` updated to Phase 0 spec
  - Removed Langflow service
  - PostgreSQL 16-alpine with health check
  - Backend service configuration
  - Frontend service configuration
  - Proper service dependencies

- [x] PostgreSQL container running and accessible
  ```bash
  docker ps | grep postgres
  # parallax-ai-postgres-1 running and healthy
  ```

- [x] Database connection verified
  ```bash
  docker exec parallax-ai-postgres-1 psql -U parallax -d parallax_ai -c '\l'
  # Shows parallax_ai database owned by parallax user
  ```

### Project Structure ✓

- [x] Backend directory structure created
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py (existing)
  │   ├── config/        ← NEW: for settings.py, prompts.py
  │   ├── auth/          ← NEW: for router.py, jwt.py, passwords.py
  │   ├── models/        ← NEW: for user.py, conversation.py, etc.
  │   ├── routers/       ← NEW: for API endpoints
  │   ├── services/      ← NEW: for claude.py, usage.py
  │   └── schemas/       ← NEW: for Pydantic models
  ├── alembic/           ← NEW: for database migrations
  ├── requirements.txt (existing)
  └── Dockerfile (existing)
  ```

- [x] Uploads directory created
  ```
  uploads/ (for user file storage)
  ```

- [x] Frontend structure verified (existing Next.js 14 app)
  ```
  frontend/
  ├── src/app/
  ├── components/
  ├── lib/
  └── public/
  ```

---

## Key Changes from Previous Architecture

### Removed
- ❌ Langflow service (AI flow builder)
- ❌ Langflow-specific environment variables
- ❌ LANGFLOW_API_URL configuration
- ❌ LANGFLOW_DATABASE_URL configuration
- ❌ Database user "langflow"
- ❌ Database name "langflow"

### Added
- ✅ Direct Anthropic API integration (via ANTHROPIC_API_KEY)
- ✅ JWT-based authentication configuration
- ✅ Backend directory structure for FastAPI application
- ✅ PostgreSQL health checks in docker-compose
- ✅ File upload configuration
- ✅ Database name "parallax_ai"
- ✅ Database user "parallax"
- ✅ Async PostgreSQL driver (postgresql+asyncpg)

---

## Environment Variables Reference

### Database
```env
POSTGRES_USER=parallax
POSTGRES_PASSWORD=<your-password>
POSTGRES_DB=parallax_ai
DATABASE_URL=postgresql+asyncpg://parallax:<password>@postgres:5432/parallax_ai
```

### Backend
```env
ANTHROPIC_API_KEY=sk-ant-api03-...     # Required for Phase 1
JWT_SECRET=<256-bit-secret>             # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=http://localhost:3000
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=<nextauth-secret>
NEXTAUTH_URL=http://localhost:3000
```

---

## Running Services

### Start PostgreSQL Only
```bash
docker-compose up -d postgres
```

### Start All Services (when Phase 1+ is implemented)
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### Reset Database (remove volume)
```bash
docker-compose down -v
docker-compose up -d postgres
```

### View Logs
```bash
docker logs parallax-ai-postgres-1
docker logs parallax-ai-backend-1      # When Phase 1 is implemented
docker logs parallax-ai-frontend-1     # When Phase 1 is implemented
```

---

## Database Access

### Connect to PostgreSQL
```bash
docker exec -it parallax-ai-postgres-1 psql -U parallax -d parallax_ai
```

### Useful PostgreSQL Commands
```sql
\l                          -- List databases
\dt                         -- List tables (empty for now)
\du                         -- List users
\q                          -- Quit
```

---

## Phase 0 Complete Criteria

All criteria from Migration Guide Phase 0 have been met:

- [x] PostgreSQL container running and accessible
- [x] Can connect to database from host machine
- [x] Project structure created per specification
- [x] Environment variables configured

---

## Next Steps: Phase 1 - Minimal Round Trip

**Goal:** Send message → Backend → Claude → Streamed response in browser

### Prerequisites for Phase 1
1. Add ANTHROPIC_API_KEY to `.env` file
2. Generate JWT_SECRET: `openssl rand -hex 32`

### Phase 1 Tasks
1. Create `backend/requirements.txt` with FastAPI dependencies
2. Create `backend/app/main.py` with minimal streaming endpoint
3. Create `backend/Dockerfile`
4. Create frontend chat test page
5. Verify round-trip streaming from Claude API

### Phase 1 Verification
- [ ] `curl localhost:8000/health` returns `{"status": "ok"}`
- [ ] Backend streams response from Claude API
- [ ] Frontend displays streamed text incrementally
- [ ] No CORS errors in browser console

---

## Files Modified in Phase 0

### Configuration Files
- `.env.example` - Updated with Phase 0 requirements
- `docker-compose.yml` - Removed Langflow, updated services

### Backend Structure
- `backend/app/config/__init__.py` - Created (empty)
- `backend/app/auth/__init__.py` - Created (empty)
- `backend/app/models/__init__.py` - Created (empty)
- `backend/app/routers/__init__.py` - Created (empty)
- `backend/app/services/__init__.py` - Created (empty)
- `backend/app/schemas/__init__.py` - Created (empty)

### Directories Created
- `backend/alembic/` - For future database migrations
- `uploads/` - For user file storage

---

## Git Commit

```
commit 32e60e9
Complete Phase 0: Infrastructure Setup

Removed Langflow and updated configuration for direct Anthropic API integration.
All verification checklists passed.
```

---

## Troubleshooting

### Issue: "role parallax does not exist"
**Solution:** The PostgreSQL volume contained old data. Fixed by running:
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d postgres  # Recreate with fresh volume
```

### Issue: Environment variables not loading
**Ensure:** `.env` file exists in project root and contains POSTGRES_PASSWORD

### Issue: Container names differ
**Note:** Docker Compose prefixes containers with directory name (`eager-pare-`)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│           NEXT.JS FRONTEND (TypeScript)             │
│  • React components, Tailwind CSS                   │
│  • Chat UI, mode selector, file upload              │
│  • Port: 3000                                       │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│           FASTAPI BACKEND (Python)                  │
│  • JWT authentication                               │
│  • Business logic: modes, usage tracking            │
│  • Port: 8000                                       │
│  • Status: Phase 1 (to be implemented)              │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                    │
│  • Database: parallax_ai                            │
│  • User: parallax                                   │
│  • Port: 5432                                       │
│  • Status: ✓ RUNNING                                │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│            ANTHROPIC CLAUDE API                     │
│  • Direct integration (no Langflow)                 │
│  • Claude Opus 4.5 / Sonnet 4.5 / Haiku 3.5        │
│  • Status: Phase 1 (to be integrated)               │
└─────────────────────────────────────────────────────┘
```

---

**Phase 0 Status:** ✅ COMPLETE

**Ready for Phase 1:** ✅ YES (pending API keys)
