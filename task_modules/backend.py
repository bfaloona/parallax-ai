"""Backend (FastAPI) development tasks."""

from invoke import task


@task
def shell(c):
    """Open Python shell in backend container (Phase 1+).

    Examples:
        inv backend.shell
    """
    print("→ backend.shell - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires backend container running")
    print("")
    print("This command will:")
    print("  1. Open interactive Python shell in backend container")
    print("  2. Pre-import common modules (SQLAlchemy, models, etc.)")
    print("")
    print("Expected command:")
    print("  docker exec -it parallax-ai-backend-1 python")


@task
def test(c, path=None, verbose=False, coverage=False):
    """Run backend tests with pytest (Phase 2+).

    Args:
        path: Specific test file or directory (optional)
        verbose: Verbose output
        coverage: Generate coverage report

    Examples:
        inv backend.test
        inv backend.test --path=tests/test_auth.py
        inv backend.test --verbose --coverage
    """
    print("→ backend.test - Phase 2+ (Database & Auth)")
    print("⚠️  Not yet implemented - requires pytest setup")
    print("")
    print("This command will:")
    if path:
        print(f"  1. Run tests in: {path}")
    else:
        print("  1. Run all backend tests")

    if coverage:
        print("  2. Generate coverage report")
        print("  3. Display coverage summary")

    if verbose:
        print("  4. Show verbose test output")

    print("")
    print("Expected command:")
    flags = []
    if verbose:
        flags.append("-v")
    if coverage:
        flags.append("--cov=app --cov-report=html --cov-report=term")
    test_path = path if path else "tests/"

    print(f"  docker exec parallax-ai-backend-1 pytest {' '.join(flags)} {test_path}")


@task
def lint(c, fix=False):
    """Run Python linters (black, flake8, mypy) (Phase 1+).

    Args:
        fix: Auto-fix issues where possible

    Examples:
        inv backend.lint
        inv backend.lint --fix
    """
    print("→ backend.lint - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires linter configuration")
    print("")
    print("This command will:")
    if fix:
        print("  1. Run black with auto-formatting")
        print("  2. Run isort with auto-fix")
    else:
        print("  1. Run black (check only)")
        print("  2. Run isort (check only)")

    print("  3. Run flake8")
    print("  4. Run mypy for type checking")
    print("")
    print("Expected commands:")
    if fix:
        print("  black backend/app")
        print("  isort backend/app")
    else:
        print("  black --check backend/app")
        print("  isort --check backend/app")
    print("  flake8 backend/app")
    print("  mypy backend/app")


@task
def migrate(c, message=None):
    """Run or create Alembic migrations (Phase 2+).

    Args:
        message: Create new migration with this message

    Examples:
        inv backend.migrate
        inv backend.migrate --message="add user roles"
    """
    print("→ backend.migrate - Phase 2+ (Database & Auth)")
    print("⚠️  Not yet implemented - requires Alembic setup")
    print("")
    if message:
        print("This command will:")
        print(f"  1. Auto-generate migration: {message}")
        print("  2. Save to backend/alembic/versions/")
        print("")
        print("Expected command:")
        print(f'  docker exec parallax-ai-backend-1 alembic revision --autogenerate -m "{message}"')
    else:
        print("This command will:")
        print("  1. Run pending migrations")
        print("  2. Update database to latest schema")
        print("")
        print("Expected command:")
        print("  docker exec parallax-ai-backend-1 alembic upgrade head")


@task
def downgrade(c, revision="base"):
    """Downgrade database to specific revision (Phase 2+).

    Args:
        revision: Target revision (default: base = empty database)

    Examples:
        inv backend.downgrade
        inv backend.downgrade --revision=-1  # Down one version
        inv backend.downgrade --revision=abc123  # Specific version
    """
    print("→ backend.downgrade - Phase 2+ (Database & Auth)")
    print("⚠️  Not yet implemented - requires Alembic setup")
    print("")
    print("This command will:")
    print(f"  1. Downgrade database to: {revision}")
    print("  2. Run down() methods in migrations")
    print("")
    print("Expected command:")
    print(f"  docker exec parallax-ai-backend-1 alembic downgrade {revision}")


@task
def routes(c):
    """List all API routes (Phase 1+).

    Examples:
        inv backend.routes
    """
    print("→ backend.routes - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires FastAPI app running")
    print("")
    print("This command will:")
    print("  1. List all registered API endpoints")
    print("  2. Show HTTP methods, paths, and handler functions")
    print("")
    print("Alternative:")
    print("  Visit http://localhost:8000/docs (FastAPI auto-docs)")


@task
def logs(c, follow=True, tail=100):
    """View backend container logs.

    Args:
        follow: Follow log output (default: True)
        tail: Number of lines to show (default: 100)

    Examples:
        inv backend.logs
        inv backend.logs --no-follow --tail=500
    """
    flags = []
    if follow:
        flags.append("-f")
    if tail:
        flags.append(f"--tail={tail}")

    cmd = f"docker-compose logs {' '.join(flags)} backend"

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def restart(c):
    """Restart backend container (Phase 1+).

    Examples:
        inv backend.restart
    """
    cmd = "docker-compose restart backend"

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def exec_bash(c):
    """Open bash shell in backend container (Phase 1+).

    Examples:
        inv backend.exec-bash
    """
    print("→ backend.exec-bash - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires backend container running")
    print("")
    container = "parallax-ai-backend-1"
    cmd = f"docker exec -it {container} /bin/bash"

    print(f"Expected command:")
    print(f"  {cmd}")
    print("")
    print("For now, use:")
    print(f"  inv docker.exec-shell --service=backend")
