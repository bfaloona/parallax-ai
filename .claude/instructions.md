# Parallax AI - Claude Code Instructions

## How to Work on This Project

### Priority Order (When in Conflict)

1. **Correctness** — Proper fix > workaround
2. **Consistency** — Match existing patterns > invent new ones
3. **Transparency** — Surface problems > hide them
4. **Speed** — Move fast only after 1-3 are satisfied

When these conflict, choose in order. A slow correct solution beats a fast workaround.

---

### Before Implementing Any Fix

Ask yourself:

1. Is this a proper solution or a workaround?
2. What else in the codebase might this affect?
3. Does this match patterns already established?

**If the answer to #1 is "workaround" — stop and tell me.** I may accept it, but I need to know.

---

### When to Pause and Ask Me

**Always ask before:**
- Adding a new dependency
- Changing database schema
- Modifying authentication flow
- Deviating from the migration guide
- Any fix that feels like a "hack"
- Deleting or significantly refactoring existing code

**Ask if uncertain:**
- Which of two valid approaches to take
- Whether a shortcut is acceptable given timeline
- If you discover the migration guide is incomplete or wrong
- If a task is taking 2x longer than expected

**Don't ask:**
- Routine implementation following established patterns
- Bug fixes with obvious correct solutions
- Formatting, linting, minor refactors

---

### After Completing Any Task

**1. Run unit tests:**
```bash
# All tests (recommended before commit)
inv test

# Unit tests only (fast, run during development)
inv test.unit

# Integration tests
inv test.integration
```

See **Testing Standards** section below for complete testing guidelines.

**2. Mental checklist:**
- [ ] Does it work? (tested, not just "looks right")
- [ ] Do all unit tests pass?
- [ ] Does it match existing code style?
- [ ] Did I change anything outside the immediate task scope?
- [ ] If yes to above — did I verify those areas still work?
- [ ] Would I be comfortable if Brandon reviewed this diff line-by-line?

**3. If tests fail:** Fix them before reporting task complete. If you can't fix them, escalate with details.

---

### Red Flags That Require Escalation

Stop and tell me if you find yourself thinking:

- "I'll just hardcode this for now"
- "This works but I'm not sure why"
- "The migration guide says X but I did Y"
- "I had to modify 5+ files for what seemed simple"
- "I'll skip this test for now"
- "This is probably fine"

These are signals something is wrong. I'd rather hear about it early.

---

## Maintaining Codebase Integrity

### After Any Code Change

1. **Run unit tests** — No exceptions
2. **Run the app** — Verify it starts without errors
3. **Test the feature** — Manual verification of what you changed

### After Multi-File Changes

When a task touches 3+ files:

1. Run the app end-to-end (not just the feature you changed)
2. Check imports aren't broken elsewhere
3. Grep for any hardcoded values you might have introduced
4. Run full test suite, not just related tests

### Consistency Checklist

| Area | Check |
|------|-------|
| **API responses** | Match schema patterns in existing endpoints |
| **Error handling** | Use established error response format |
| **Database queries** | Follow async patterns from Phase 2 |
| **Frontend state** | Match existing state management approach |
| **Environment vars** | Add to `.env.example` if new |
| **Types** | No `any` in TypeScript without justification |

### When You Spot Technical Debt

Don't silently fix it. Instead:

1. Note what you found
2. Ask if I want it fixed now or tracked for later
3. If tracked, add a `# TODO(debt): [description]` comment

---

## Working with This Project

### Starting a Phase

1. **Read** the relevant phase in `docs/MIGRATION_GUIDE.md`
2. **Identify** verification criteria (the "Phase Complete When" checklist)
3. **Tell me your plan** before writing code — 2-3 sentences is fine
4. **Implement** incrementally, testing as you go
5. **Run tests** after each significant change
6. **Run full verification** checklist
7. **Report completion** using the format below

### Mid-Phase Check-ins

For phases estimated >2 hours, check in halfway:

**If smooth:**
> "Completed X and Y. All tests passing. Starting Z. No blockers."

**If blocked:**
> "Hit issue with X. Options are A or B. Recommend A because [reason]. Tests currently failing on [area]."

### Ending a Phase

When a phase is complete and approved:

1. **Create completion documentation**: `docs/PHASE_NN_COMPLETE.md`
2. **Commit the completion**: Include all phase work and the completion doc
3. **Provide phase report** (see format below)

**Phase completion document format** (`docs/PHASE_NN_COMPLETE.md`):

```markdown
# Phase N: [Phase Name] - COMPLETE

**Completion Date:** YYYY-MM-DD

## Summary

[1-2 paragraph overview of what was accomplished]

## Implemented

- [Detailed list of what was built]
- [Include file paths for key changes]

## Tests

- [X] Backend tests: N passed, M skipped
- [X] Frontend tests: N passed (if applicable)
- [X] Manual verification: [list what was tested]
- [X] Coverage: XX% (threshold: 65%)

## Verification Checklist

From "Phase N Complete When" criteria:
- [X] [Criterion 1]
- [X] [Criterion 2]
- [ ] [Deferred item with explanation]

## Key Files Changed

- `path/to/file1.py` - [Brief description]
- `path/to/file2.py` - [Brief description]

## Known Issues / Technical Debt

- [Issue 1 with explanation and plan]
- [Or "None"]

## Migration Notes

[Any important notes for future phases or deployment]

## Ready for Next Phase

Yes/No - [Brief explanation if No]
```

**Phase report format** (for chat):

```
## Phase N Complete

**Implemented:**
- [list of what was built]

**Tests:**
- [X] Backend tests passing (N tests)
- [X] Frontend tests passing (N tests)
- [X] Manual verification complete

**Verified:**
- [list of checks performed from "Phase Complete When"]

**Files Changed:**
- [list key files, helps me review]

**Concerns/Notes:**
- [anything I should know, or "None"]

**Ready for Phase N+1:** Yes/No
```

---

## Project Overview

**Parallax AI** is a technical design assistant being migrated from a Poe Canvas app to a self-hosted FastAPI + Next.js application.

**Tech Stack:**
- Backend: FastAPI (Python 3.11+) + PostgreSQL 16 + SQLAlchemy 2.0
- Frontend: Next.js 14 (TypeScript, Tailwind CSS)
- LLM: Direct Anthropic Claude API (no Langflow)
- Auth: NextAuth.js with credentials provider
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

**Critical:** Never hardcode prompts in handlers. Always use `get_system_prompt(mode)`.

---

## Key Features

1. **Chat System** — Streaming responses (SSE), conversation persistence, message history
2. **Technical Drawings** — Parse `drawing-2d` (Rough.js) and `drawing-3d` (Three.js) code blocks
3. **File Upload** — Drag & drop, 10MB limit, user-specific storage
4. **Model Selection** — Opus/Sonnet/Haiku with cost indicators
5. **Search & Export** — Global search (Cmd+K), PDF export
6. **Responsive UI** — Dark/light theme, mobile-friendly, brand colors

---

## Code Style

### Backend (Python/FastAPI)

```python
# ✓ Async/await throughout
async def get_conversation(id: UUID, db: AsyncSession) -> Conversation:
    
# ✓ Type hints required
def create_token(user_id: str) -> str:

# ✓ Pydantic for validation
class ChatRequest(BaseModel):
    content: str
    model: str = "sonnet"

# ✓ JWT auth via dependency injection
@router.get("/{id}")
async def get(id: UUID, user_id: str = Depends(get_current_user)):
```

### Frontend (TypeScript/Next.js)

```typescript
// ✓ Strict TypeScript - avoid 'any'
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

// ✓ Client components marked explicitly
'use client';

// ✓ Tailwind for styling - match existing patterns
<button className="px-4 py-2 bg-teal-600 rounded hover:bg-teal-700">
```

---

## Testing Standards

### Test Infrastructure

We use **pytest** with industry-standard practices:

```bash
# Run all tests
inv test

# Run unit tests only (fast)
inv test.unit

# Run integration tests
inv test.integration

# Run acceptance tests (Selenium)
inv test.acceptance
```

### Test Organization

```
tests/
├── unit/           # Fast, isolated tests (< 1s each)
├── integration/    # Database, API tests
└── acceptance/     # End-to-end Selenium tests (~5 total)
```

### Test Naming Convention

**CRITICAL**: Use rigid naming that clearly states functionality under test:

```python
def test_<functionality>_<condition>_<expected_result>():
    """One-line description of what this tests."""
```

**Examples:**
```python
# ✓ GOOD - Clear, specific, states expected result
def test_chat_endpoint_valid_message_returns_200():
def test_user_auth_invalid_token_returns_401():
def test_database_connection_timeout_raises_error():

# ❌ BAD - Vague, unclear what's being tested
def test_chat():
def test_api():
def test_user_login_works():
```

### What to Test

**DO test:**
- ✓ Your code and your configuration
- ✓ API endpoints (inputs, outputs, error cases)
- ✓ Business logic and data transformations
- ✓ Database interactions and persistence
- ✓ Authentication and authorization
- ✓ Error handling and edge cases

**DON'T test:**
- ✗ Library code (FastAPI, SQLAlchemy, Anthropic SDK)
- ✗ Third-party APIs (mock them instead)
- ✗ Language features (Python, TypeScript)
- ✗ Framework internals

### Test Types

#### Unit Tests (`@pytest.mark.unit`)

**Characteristics:**
- Fast (< 1s per test)
- No database, no external services
- Use mocks for dependencies
- Test one function/class in isolation

**Example:**
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_endpoint_valid_message_calls_anthropic_with_correct_model(client):
    with patch('backend.app.main.client.messages.stream') as mock_stream:
        mock_stream.return_value = mock_streaming_response()

        await client.post("/api/chat", json={"message": "test"})

        call_args = mock_stream.call_args
        assert call_args.kwargs["model"] == "claude-sonnet-4-20250514"
```

#### Integration Tests (`@pytest.mark.integration`)

**Characteristics:**
- Test component interactions
- Use real database (test instance)
- Test API endpoints end-to-end
- Verify data persistence

**Example:**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_conversation_create_and_retrieve_persists_to_database(db_session):
    # Create conversation
    conv = await create_conversation(user_id="test", title="Test")

    # Retrieve from database
    retrieved = await get_conversation(conv.id)

    assert retrieved.title == "Test"
    assert retrieved.user_id == "test"
```

#### Acceptance Tests (`@pytest.mark.acceptance`)

**Characteristics:**
- End-to-end user workflows
- Use Selenium WebDriver
- Test against running application
- **Limited to ~5 critical journeys**

**Example:**
```python
@pytest.mark.acceptance
def test_user_can_send_message_and_receive_response(browser):
    # Navigate to app
    browser.get("http://localhost:3000")

    # Type message
    input_box = browser.find_element(By.ID, "chat-input")
    input_box.send_keys("Hello")
    input_box.submit()

    # Verify response appears
    response = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "assistant-message"))
    )
    assert response.text != ""
```

### Test Requirements

| When | Requirement |
|------|-------------|
| After any code change | Run `inv test.unit` |
| Before committing | Run `inv test` (all tests) |
| After updating dependencies | Run `inv test` + verify app runs |
| After Docker rebuild | Run `inv test` + verify containers |
| Before completing any phase | Run `inv test` + all manual verifications |

### Coverage Requirements

- **Minimum coverage**: 80% (enforced by pytest.ini)
- **Focus areas**: API endpoints, business logic, auth
- **View coverage**: `coverage_html/index.html` after running tests

### Writing Tests - Best Practices

1. **Write tests alongside code** - Not as an afterthought
2. **One assertion per test** - Keep tests focused
3. **Use descriptive names** - Follow naming convention rigorously
4. **Test behavior, not implementation** - Focus on outputs, not internals
5. **Keep tests independent** - No test should depend on another
6. **Use fixtures for setup** - Defined in `tests/conftest.py`
7. **Mock external services** - Never hit real APIs in tests

### Test Failures - Non-Negotiable Rules

**All tests MUST either pass or be explicitly skipped with justification.**

- ✅ **DO** write tests that validate your code and configuration
- ✅ **DO** skip tests that lack infrastructure (document why and when they'll be enabled)
- ✅ **DO** ensure a test validates actual behavior to pass - never shortcut to make it pass
- ❌ **NEVER** mark a task complete with failing tests
- ❌ **NEVER** delete tests to make them pass
- ❌ **NEVER** commit code that breaks existing tests
- ❌ **NEVER** add tests that can't be useful yet (wait until infrastructure exists)
- ❌ **NEVER** use fake assertions or shortcuts to make tests pass

**If you must skip a test:**
```python
# ✓ GOOD - Clear reason and plan
pytestmark = pytest.mark.skip(
    reason="UUID type incompatible with SQLite - covered by integration tests"
)

# ❌ BAD - No explanation
@pytest.mark.skip
def test_something():
```

**Test integrity principles:**
1. A passing test must validate real code or configuration behavior
2. Tests without necessary infrastructure should be skipped, not written
3. All tests must pass OR be skipped - no exceptions
4. If a test seems wrong, ask before modifying it

### Running Tests

```bash
# Fast iteration during development
inv test.unit

# Full validation before commit
inv test

# With coverage report
inv test --coverage

# Stop on first failure
inv test --failfast

# Run specific test file
inv test.unit --path=tests/unit/test_api_chat.py

# Verbose output
inv test --verbose

# Acceptance tests (requires running app)
inv docker.up
inv test.acceptance
```

---

## Critical Implementation Notes

### Mode System
- **Never hardcode prompts** — Import from `backend/app/config/prompts.py`
- Use `get_system_prompt(mode)` helper
- Mode changes persist on conversation record

### Technical Drawings
- ~800 lines to port from original Poe app
- Rough.js for sketchy 2D, Three.js for 3D
- **Must dispose Three.js scenes** to prevent memory leaks
- Test memory cleanup when switching conversations

### File Upload
- Validate MIME types server-side
- Store: `/uploads/{user_id}/{file_id}.{ext}`
- Serve via `/api/files/{file_id}` — never expose filesystem paths
- Test with files at size limit (10MB)

### Security
- Verify user ownership before every DB operation
- 256-bit JWT secret (use `openssl rand -hex 32`)
- CORS limited to allowed origins only
- HTTPS enforced in production
- Never log sensitive data (tokens, passwords, API keys)

---

## Naming Conventions - Branch Directory Independence

**CRITICAL**: Claude Code runs in temporary git worktrees with auto-generated names (e.g., `eager-pare`, `unruffled-shirley`). These names change between sessions.

**NEVER** hardcode branch directory names:

```python
# ❌ BAD - Will break in next session
container_name = "eager-pare-backend-1"
path = "/Users/user/.claude-worktrees/parallax-ai/eager-pare/uploads"

# ✓ GOOD - Works everywhere
c.run("docker-compose exec backend /bin/sh")
upload_dir = "./uploads"  # or os.getenv("UPLOAD_DIR")
```

**Solution:** Set explicit project name in docker-compose.yml:

```yaml
version: '3.8'
name: parallax-ai  # ✓ Fixed project name

services:
  postgres:
    # Containers always named: parallax-ai-postgres-1
```

---

## Common Pitfalls (Learned from Phase 1)

### Docker Environment Variables

Variables in `environment:` with `${VAR}` get substituted from **shell**, NOT from .env file:

```yaml
# ❌ BAD - Overrides .env if $API_KEY not in shell
env_file: .env
environment:
  API_KEY: ${API_KEY}

# ✓ GOOD - Let env_file handle it
env_file: .env
environment:
  CORS_ORIGINS: http://localhost:3000  # Literal values OK
```

**Debug:** `docker-compose config | grep API_KEY`

### Python Dependencies

- Check Python version compatibility (3.11 vs 3.13)
- Pin exact versions in requirements.txt
- Test `docker build` before `docker-compose up`

**Known working versions (Jan 2025):**
```
fastapi==0.115.6
uvicorn[standard]==0.32.1
anthropic==0.42.0
pydantic==2.10.3
httpx==0.27.2
```

### Anthropic API

- Model IDs change — verify against current docs
- Current models: `claude-sonnet-4-20250514`, `claude-opus-4-5-20251101`
- Test with curl before integrating

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' \
  --max-time 10
```

---

## Testing Requirements

### When to Run Tests

| Action | Run Tests? |
|--------|-----------|
| After any code change | Yes |
| Before committing | Yes |
| After resolving merge conflicts | Yes |
| After updating dependencies | Yes |
| After Docker rebuild | Yes |

### Test Commands

```bash
# Backend unit tests
cd backend && pytest

# Backend with coverage
cd backend && pytest --cov=app --cov-report=term-missing

# Frontend unit tests
cd frontend && npm test

# Frontend watch mode (during development)
cd frontend && npm test -- --watch

# All tests (run before completing any phase)
cd backend && pytest && cd ../frontend && npm test
```

### Test Failures

- **Never** mark a task complete with failing tests
- **Never** skip or delete tests to make them pass
- If a test seems wrong, ask before modifying it
- If you can't fix a failure, escalate with:
  - Which test is failing
  - The error message
  - What you've tried

---

## Reference Documents

📄 **`docs/MIGRATION_GUIDE.md`** — Primary reference containing:
- 11 development phases with complete code
- Database schemas
- API endpoint specifications
- Component examples
- Brand guidelines (colors, typography)
- Deployment instructions
- "Phase Complete When" checklists

**Always check the migration guide first** before implementing. It has answers to most questions.

---

## Success Criteria

Migration complete when:

- [ ] All 7 modes work with distinct behavior
- [ ] Technical drawings render (2D + 3D)
- [ ] File upload functional
- [ ] Search and export working
- [ ] Responsive UI matches brand
- [ ] All unit tests passing
- [ ] Deployed to production with SSL
- [ ] End-to-end smoke test passes on production

---

## Quick Reference

### Commands

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run backend tests
docker-compose exec backend pytest

# Run frontend tests  
cd frontend && npm test

# Check container status
docker-compose ps

# Rebuild after dependency changes
docker-compose build --no-cache backend
```

### Key Files

```
backend/
├── app/config/prompts.py    # Mode system prompts
├── app/auth/jwt.py          # Authentication
├── app/routers/             # API endpoints
└── tests/                   # Backend tests

frontend/
├── components/              # React components
├── lib/api.ts              # API client
└── __tests__/              # Frontend tests

docs/
└── MIGRATION_GUIDE.md      # Phase-by-phase instructions
```

### Environment Variables

Required in `.env`:
```
DATABASE_URL=postgresql+asyncpg://...
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=[256-bit hex]
CORS_ORIGINS=http://localhost:3000
```

---

## Summary: The Prime Directives

1. **Test after every change** — No exceptions
2. **Match existing patterns** — Consistency over cleverness  
3. **Escalate workarounds** — I need to know about hacks
4. **Follow the migration guide** — It has the answers
5. **Report completions properly** — Use the template above

When in doubt, ask. I'd rather answer a question than debug a workaround.
