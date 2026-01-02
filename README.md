# Parallax AI

**Technical design assistant with 7 distinct thinking modes for engineering work**

Parallax AI is a full-stack application built with **FastAPI**, **Next.js**, and **PostgreSQL**, featuring direct integration with the Anthropic Claude API.

## 🏗 Architecture

- **Frontend**: Next.js 14 (React, TypeScript, Tailwind CSS) - Port `3000`
- **Backend**: FastAPI (Python 3.11+, async/await) - Port `8000`
- **Database**: PostgreSQL 16 - Port `5432`
- **LLM**: Direct Anthropic Claude API (Opus 4.5, Sonnet 4.5, Haiku 3.5)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- Git

### New Developer Setup

```bash
# One-command setup
pip install -r requirements-dev.txt
inv dev.setup

# Edit .env file to add your API keys
# - ANTHROPIC_API_KEY=sk-ant-api03-...
# - JWT_SECRET (generate with: inv dev.secrets)

# Verify everything works
inv dev.check

# Start services
inv docker.up
```

### Daily Development

```bash
# Start all services
inv docker.up

# View logs
inv docker.logs

# Connect to database
inv db.shell

# Run tests (Phase 1+)
inv dev.test

# See all available commands
inv --list
```

**Detailed command documentation**: See [`docs/DEVELOPER_COMMANDS.md`](docs/DEVELOPER_COMMANDS.md)

### Access Services

- Frontend: [http://localhost:3000](http://localhost:3000) *(Phase 1+)*
- Backend API: [http://localhost:8000](http://localhost:8000) *(Phase 1+)*
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs) *(Phase 1+)*
- Database: `localhost:5432` (use `inv db.shell` to connect)

## 📂 Project Structure

```
parallax-ai/
├── backend/
│   ├── app/
│   │   ├── config/      # Settings, prompts
│   │   ├── auth/        # JWT authentication
│   │   ├── models/      # Database models
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   └── schemas/     # Pydantic models
│   ├── alembic/         # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/app/         # Next.js 14 app router
│   ├── components/      # React components
│   ├── lib/             # Utilities
│   └── public/          # Static assets
├── tasks/               # Invoke task modules
│   ├── docker.py        # Docker commands
│   ├── db.py            # Database commands
│   ├── dev.py           # Development workflow
│   ├── backend.py       # Backend tasks
│   └── frontend.py      # Frontend tasks
├── docs/
│   ├── MIGRATION_GUIDE.md        # 11-phase implementation guide
│   ├── DEVELOPER_COMMANDS.md     # Complete command reference
│   ├── PHASE_0_COMPLETE.md       # Phase 0 status
│   └── BRANDING.md               # Logo and brand guidelines
├── tasks.py             # Main invoke entry point
├── docker-compose.yml
├── requirements-dev.txt # Development dependencies (invoke, etc.)
└── .env.example
```

## 📖 Documentation

- **[Developer Commands](docs/DEVELOPER_COMMANDS.md)** - Complete command reference and workflows
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - 11-phase implementation plan
- **[Phase 0 Status](docs/PHASE_0_COMPLETE.md)** - Infrastructure setup (COMPLETE ✅)
- **[Branding Guide](docs/BRANDING.md)** - Logo, colors, typography

## 🎯 7-Mode System

Parallax AI's core feature is a **7-mode system** providing distinct intellectual stances:

| Mode | Stance | Purpose |
|------|--------|---------|
| **Balanced** | Direct generalist | Standard problem-solving |
| **Challenge** | Skeptical stress-tester | Find flaws and edge cases |
| **Explore** | Neutral researcher | Gather information objectively |
| **Ideate** | Creative generator | Brainstorm possibilities |
| **Clarify** | Socratic questioner | Understand requirements |
| **Plan** | Pragmatic sequencer | Create actionable steps |
| **Audit** | Feasibility analyst | Assess costs and constraints |

## ☁️ Deployment (Coolify)

Deployment configuration for **Coolify** on Hetzner VPS (see Phase 11 in Migration Guide).

**Production Environment Variables**:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `JWT_SECRET` - 256-bit secret (generate with `inv dev.secrets`)
- `DATABASE_URL` - PostgreSQL connection string
- `NEXT_PUBLIC_API_URL` - Backend URL (e.g., `https://api.parallax.yourdomain.com`)

**Domains**:
- Frontend: `app.parallax.yourdomain.com` → Port `3000`
- Backend API: `api.parallax.yourdomain.com` → Port `8000`

## 🧑‍💻 Development Phases

**Current Status: Phase 0 Complete ✅**

1. ✅ **Phase 0**: Infrastructure Setup
2. ⏳ **Phase 1**: Minimal Round Trip (FastAPI + Claude streaming)
3. ⏳ **Phase 2**: Database & Auth
4. ⏳ **Phase 3**: Conversation CRUD
5. ⏳ **Phase 4**: Mode System
6. ⏳ **Phase 5**: Model Selection
7. ⏳ **Phase 6**: File Upload
8. ⏳ **Phase 7**: Technical Drawings
9. ⏳ **Phase 8**: UI Polish
10. ⏳ **Phase 9**: Search & Export
11. ⏳ **Phase 10**: Help System
12. ⏳ **Phase 11**: Production Deployment

See [`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md) for detailed implementation plan.

## 🛠 Technology Stack

**Backend:**
- FastAPI (async Python framework)
- SQLAlchemy 2.0 (async ORM)
- Alembic (migrations)
- Anthropic Python SDK
- JWT authentication

**Frontend:**
- Next.js 14 (App Router)
- React Server Components
- TypeScript
- Tailwind CSS
- Server-Sent Events (SSE) for streaming

**Infrastructure:**
- PostgreSQL 16
- Docker & Docker Compose
- Hetzner VPS (CPX21)
- Coolify (deployment orchestration)

## 📝 License

*Add license information here*

## 🤝 Contributing

Development workflow managed via `invoke` commands. See [`docs/DEVELOPER_COMMANDS.md`](docs/DEVELOPER_COMMANDS.md) for details.
