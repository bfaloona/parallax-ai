# Parallax AI Developer Commands

Complete reference for development workflow commands using Python `invoke`.

## Quick Start

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# First-time setup
inv dev.setup

# List all commands
inv --list

# Get help for a command
inv --help docker.up
```

---

## Table of Contents

1. [Development Workflow](#development-workflow) (dev.*)
2. [Docker & Infrastructure](#docker--infrastructure) (docker.*)
3. [Database Management](#database-management) (db.*)
4. [Backend Tasks](#backend-tasks) (backend.*) - Phase 1+
5. [Frontend Tasks](#frontend-tasks) (frontend.*) - Phase 1+
6. [Advanced Scenarios](#advanced-scenarios)

---

## Development Workflow

### `inv dev.setup`
**Initial project setup for new developers**

Automated setup that:
1. Checks all prerequisites (Docker, Node, Python, Git)
2. Creates `.env` file from template
3. Installs development dependencies
4. Starts PostgreSQL

```bash
inv dev.setup
```

After running, you'll need to manually:
- Add `ANTHROPIC_API_KEY` to `.env`
- Generate and add `JWT_SECRET` with `inv dev.secrets`

---

### `inv dev.check`
**Verify all development prerequisites**

Checks for:
- Docker & Docker Compose
- Node.js
- Python
- Git
- `.env` file and critical environment variables
- Running Docker containers

```bash
inv dev.check

# Example output:
# ✓ Docker               Docker version 29.1.3
# ✓ Node.js              v24.10.0
# ✓ Python               Python 3.13.3
# ✓ .env file            Found
# ✓ ANTHROPIC_API_KEY    Configured
# ⚠️  JWT_SECRET          Not set
```

---

### `inv dev.secrets`
**Generate secure random secrets for JWT and authentication**

```bash
# Print secrets only
inv dev.secrets

# Auto-update .env file
inv dev.secrets --update-env
```

Generates:
- `JWT_SECRET` (256-bit hex)
- `NEXTAUTH_SECRET` (256-bit hex)

---

### `inv dev.test` *(Phase 1+)*
**Run all tests (backend + frontend)**

```bash
inv dev.test
```

Currently a stub. Will be implemented in Phase 1.

---

### `inv dev.lint` *(Phase 1+)*
**Run all linters across codebase**

```bash
# Check only
inv dev.lint

# Auto-fix where possible
inv dev.lint --fix
```

Will run:
- Python: black, flake8, mypy
- TypeScript: ESLint, Prettier

---

### `inv dev.clean`
**Clean up caches, generated files, and temporary data**

```bash
inv dev.clean
```

Removes:
- `__pycache__` directories
- `.pytest_cache`, `.mypy_cache`
- `node_modules/.cache`
- `.next` build directories

---

## Docker & Infrastructure

### `inv docker.up`
**Start all services or specific service**

```bash
# Start all services in detached mode
inv docker.up

# Start in foreground (see logs)
inv docker.up --no-detach

# Start only PostgreSQL
inv docker.up --service=postgres

# Start only backend
inv docker.up --service=backend
```

---

### `inv docker.down`
**Stop all services**

```bash
# Stop services (preserve data)
inv docker.down

# Stop and remove volumes (DELETE DATA!)
inv docker.down --volumes

# Don't remove orphan containers
inv docker.down --no-remove-orphans
```

⚠️  **Warning:** `--volumes` flag will **delete all database data**!

---

### `inv docker.restart`
**Restart services**

```bash
# Restart all services
inv docker.restart

# Restart specific service
inv docker.restart --service=backend
```

---

### `inv docker.logs`
**View service logs**

```bash
# Follow all logs (last 100 lines)
inv docker.logs

# View specific service
inv docker.logs --service=postgres

# Show more lines
inv docker.logs --tail=500

# Don't follow (just print and exit)
inv docker.logs --no-follow
```

---

### `inv docker.ps`
**List running containers**

```bash
inv docker.ps
```

---

### `inv docker.build`
**Build or rebuild service images**

```bash
# Build all services
inv docker.build

# Build specific service
inv docker.build --service=backend

# Build without cache (fresh build)
inv docker.build --no-cache
```

---

### `inv docker.clean`
**Remove all containers, volumes, and orphans (DESTRUCTIVE)**

```bash
# With confirmation prompt
inv docker.clean

# Skip confirmation
inv docker.clean --no-confirm
```

⚠️  **Warning:** This will **delete all data and containers**!

---

### `inv docker.exec-shell`
**Execute a shell in a running container**

```bash
# Open shell in backend container
inv docker.exec-shell --service=backend

# Open shell in postgres container as postgres user
inv docker.exec-shell --service=postgres --user=postgres
```

---

## Database Management

### `inv db.shell`
**Connect to PostgreSQL interactive shell**

```bash
inv db.shell
```

Once connected, you can run SQL commands:
```sql
\l                  -- List databases
\dt                 -- List tables
\d users            -- Describe users table
SELECT * FROM users;
\q                  -- Quit
```

---

### `inv db.reset`
**Reset database (drops and recreates)**

```bash
# With confirmation prompt
inv db.reset

# Skip confirmation
inv db.reset --no-confirm
```

⚠️  **Warning:** This will **delete all database data**!

Useful when:
- Database is in a corrupted state
- Need to start fresh with migrations
- Testing database initialization

---

### `inv db.backup`
**Backup database to SQL file**

```bash
# Auto-generated filename (backup_YYYYMMDD_HHMMSS.sql)
inv db.backup

# Custom filename
inv db.backup --filename=before_migration.sql
```

---

### `inv db.restore`
**Restore database from SQL backup**

```bash
inv db.restore --filename=backup_20260102_120000.sql
```

⚠️  **Warning:** This will **replace all current data**!

---

### `inv db.init` *(Phase 2+)*
**Initialize database schema with Alembic migrations**

```bash
inv db.init
```

Currently a stub. Will be implemented in Phase 2.

---

### `inv db.migrate` *(Phase 2+)*
**Run or create database migrations**

```bash
# Run pending migrations
inv db.migrate

# Create new migration
inv db.migrate --message="add user roles"
```

Currently a stub. Will be implemented in Phase 2.

---

### `inv db.status`
**Show database connection status and basic info**

```bash
inv db.status

# Example output:
# ✓ Container 'parallax-ai-postgres-1' is running
# ✓ Database 'parallax_ai' is accessible
#   Tables: 5
```

---

## Backend Tasks

> **Note:** Most backend tasks require Phase 1+ implementation

### `inv backend.shell` *(Phase 1+)*
**Open Python shell in backend container**

```bash
inv backend.shell
```

---

### `inv backend.test` *(Phase 2+)*
**Run backend tests with pytest**

```bash
# Run all tests
inv backend.test

# Run specific test file
inv backend.test --path=tests/test_auth.py

# Verbose output with coverage
inv backend.test --verbose --coverage
```

---

### `inv backend.lint` *(Phase 1+)*
**Run Python linters**

```bash
# Check only
inv backend.lint

# Auto-fix
inv backend.lint --fix
```

---

### `inv backend.migrate` *(Phase 2+)*
**Alembic migrations (run or create)**

```bash
# Run pending migrations
inv backend.migrate

# Create new migration
inv backend.migrate --message="add conversation timestamps"
```

---

### `inv backend.downgrade` *(Phase 2+)*
**Downgrade database schema**

```bash
# Downgrade to empty database
inv backend.downgrade

# Downgrade one version
inv backend.downgrade --revision=-1

# Downgrade to specific version
inv backend.downgrade --revision=abc123def
```

---

### `inv backend.routes` *(Phase 1+)*
**List all API routes**

```bash
inv backend.routes
```

Alternative: Visit http://localhost:8000/docs for interactive API documentation.

---

### `inv backend.logs`
**View backend container logs**

```bash
inv backend.logs

# Options: --no-follow, --tail=N
```

---

### `inv backend.restart` *(Phase 1+)*
**Restart backend container**

```bash
inv backend.restart
```

---

### `inv backend.exec-bash` *(Phase 1+)*
**Open bash shell in backend container**

```bash
inv backend.exec-bash
```

---

## Frontend Tasks

> **Note:** Most frontend tasks require Phase 1+ implementation

### `inv frontend.shell` *(Phase 1+)*
**Open shell in frontend container**

```bash
inv frontend.shell
```

---

### `inv frontend.test` *(Phase 1+)*
**Run frontend tests**

```bash
# Run all tests
inv frontend.test

# Watch mode
inv frontend.test --watch

# With coverage
inv frontend.test --coverage
```

---

### `inv frontend.lint` *(Phase 1+)*
**Run ESLint and Prettier**

```bash
# Check only
inv frontend.lint

# Auto-fix
inv frontend.lint --fix
```

---

### `inv frontend.type-check` *(Phase 1+)*
**Run TypeScript type checking**

```bash
inv frontend.type-check
```

---

### `inv frontend.build` *(Phase 1+)*
**Build frontend for production**

```bash
# Production build
inv frontend.build

# Development build
inv frontend.build --no-production
```

---

### `inv frontend.logs`
**View frontend container logs**

```bash
inv frontend.logs

# Options: --no-follow, --tail=N
```

---

### `inv frontend.restart` *(Phase 1+)*
**Restart frontend container**

```bash
inv frontend.restart
```

---

### `inv frontend.analyze` *(Phase 8+)*
**Analyze bundle size**

```bash
inv frontend.analyze
```

---

### `inv frontend.storybook` *(Phase 8+)*
**Run or build Storybook**

```bash
# Dev server
inv frontend.storybook

# Build static site
inv frontend.storybook --build
```

---

## Advanced Scenarios

### Scenario: Database Migration Failed

```bash
# 1. Check current migration status
inv db.shell
# In psql: SELECT * FROM alembic_version;
# \q

# 2. If corrupted, reset and re-run migrations
inv db.reset
inv db.init

# 3. Or restore from backup
inv db.restore --filename=before_migration.sql
```

---

### Scenario: Port Conflict (port 5432, 8000, or 3000 in use)

```bash
# Find process using port 5432
lsof -i :5432

# Kill the process
kill -9 <PID>

# Or stop all Docker containers
inv docker.down
inv docker.up
```

---

### Scenario: Container Won't Start

```bash
# View logs to diagnose
inv docker.logs --service=backend --tail=500

# Rebuild image without cache
inv docker.build --service=backend --no-cache

# Clean everything and start fresh
inv docker.clean
inv docker.up
```

---

### Scenario: Database Connection Refused

```bash
# Check database status
inv db.status

# Wait for database to be ready (may take 5-10 seconds)
docker logs parallax-ai-postgres-1

# Reset database if still failing
inv db.reset
```

---

### Scenario: Need Fresh Development Environment

```bash
# Nuclear option: clean everything
inv docker.clean --no-confirm
inv dev.clean

# Rebuild from scratch
inv dev.setup
inv docker.build --no-cache
inv docker.up
```

---

### Scenario: Debugging Backend Code

```bash
# 1. Stop backend container
docker-compose stop backend

# 2. Run backend locally with debugger
cd backend
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload

# 3. Attach debugger from IDE to localhost:5678
```

---

### Scenario: Testing with Production-like Data

```bash
# 1. Backup current dev database
inv db.backup --filename=dev_backup.sql

# 2. Get production data (sanitized dump from DevOps)
# Download sanitized_prod.sql

# 3. Restore
inv db.restore --filename=sanitized_prod.sql

# 4. When done, restore dev data
inv db.restore --filename=dev_backup.sql
```

---

### Scenario: Inspecting Docker Network Issues

```bash
# List networks
docker network ls

# Inspect network
docker network inspect parallax-ai_default

# Check container connectivity
docker exec parallax-ai-backend-1 ping postgres

# Check DNS resolution
docker exec parallax-ai-backend-1 nslookup postgres
```

---

### Scenario: Volume Inspection

```bash
# List volumes
docker volume ls

# Inspect postgres volume
docker volume inspect parallax-ai_postgres_data

# Manually backup volume
docker run --rm -v parallax-ai_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Manually restore volume
docker run --rm -v parallax-ai_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

---

## Command Quick Reference

### Daily Development
```bash
inv docker.up              # Start services
inv docker.logs            # View logs
inv db.shell               # Database access
inv backend.test           # Run tests (Phase 1+)
inv dev.check              # Verify setup
```

### Before Committing
```bash
inv dev.lint --fix         # Fix linting issues (Phase 1+)
inv dev.test               # Run all tests (Phase 1+)
inv frontend.type-check    # Check types (Phase 1+)
```

### Troubleshooting
```bash
inv db.status              # Check database
inv docker.ps              # List containers
inv docker.logs --service=backend  # View service logs
inv docker.restart         # Restart all
inv docker.clean           # Nuclear option
```

### Database Operations
```bash
inv db.backup              # Before risky operations
inv db.restore             # Recover from backup
inv db.reset               # Fresh start
inv db.migrate             # Update schema (Phase 2+)
```

---

## Environment Variables Reference

See `.env.example` for all available variables.

**Critical variables:**
- `ANTHROPIC_API_KEY` - Required for Phase 1+
- `JWT_SECRET` - Generate with `inv dev.secrets`
- `DATABASE_URL` - Auto-configured for Docker
- `POSTGRES_PASSWORD` - Set in `.env`

---

## Getting Help

```bash
# List all commands
inv --list

# Get help for a specific command
inv --help docker.up

# View command source code
cat tasks/docker.py
```

---

## Troubleshooting Command Issues

**"Module 'invoke' not found"**
```bash
pip install -r requirements-dev.txt
```

**"Collection 'docker' not found"**
```bash
# Ensure you're in project root
ls tasks.py  # Should exist
```

**"Permission denied" on Docker commands**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Then log out and back in
```

---

## Contributing New Commands

See `tasks/docker.py` for examples. Follow these patterns:

1. **Print the command** before executing:
   ```python
   print(f"→ Running: {cmd}")
   ```

2. **Hide secrets** in output:
   ```python
   # Good: Don't print passwords
   print(f"→ Running: psql -U user -d database")
   # Bad: print(f"→ Running: psql -U user -p{password}")
   ```

3. **Use `pty=True`** for interactive commands:
   ```python
   c.run(cmd, pty=True)
   ```

4. **Document with docstrings** and examples:
   ```python
   @task
   def my_task(c, arg=None):
       """Short description.

       Args:
           arg: Argument description

       Examples:
           inv my.task
           inv my.task --arg=value
       """
   ```

---

## Additional Resources

- **Migration Guide**: `docs/MIGRATION_GUIDE.md`
- **Phase 0 Status**: `docs/PHASE_0_COMPLETE.md`
- **Branding Guide**: `docs/BRANDING.md`
- **Project README**: `README.md`

---

*Last updated: Phase 0 complete (January 2, 2026)*
