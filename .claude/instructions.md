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
