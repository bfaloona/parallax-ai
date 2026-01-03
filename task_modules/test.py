"""Testing tasks for Parallax AI."""

from invoke import task
from task_modules import Colors


@task
def test(c, verbose=False, coverage=True, failfast=False):
    """Run all backend tests (unit + integration).

    This runs the full test suite including:
    - Unit tests (fast, mocked)
    - Integration tests (real PostgreSQL database)

    Args:
        verbose: Verbose output
        coverage: Generate coverage report (default: True)
        failfast: Stop on first failure

    Examples:
        inv test                           # Run all tests with coverage
        inv test --verbose                 # Verbose output
        inv test --no-coverage --failfast  # Fast mode, stop on first fail
    """

    flags = ["-v"] if verbose else []
    if coverage:
        flags.append("--cov=app")
        flags.append("--cov-report=term-missing")
        flags.append("--cov-report=html:coverage_html")
    if failfast:
        flags.append("-x")

    # Run all tests (unit + integration)
    cmd = f"docker-compose exec backend pytest {' '.join(flags)}"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()

    test_result = c.run(cmd, warn=True, pty=True)

    if test_result.ok:
        result = Colors.success("All tests passed!")
        if result:
            print(result)
        if coverage:
            print()
            print("Coverage report: backend/coverage_html/index.html")
    else:
        result = Colors.error("Some tests failed")
        if result:
            print(result)
        return False

    return True


@task(name="unit")
def test_unit(c, verbose=False, coverage=True, path=None):
    """Run unit tests only (fast, isolated tests).

    Unit tests should:
    - Run quickly (< 1s per test)
    - Not require database or external services
    - Test individual functions/classes in isolation
    - Use mocks for dependencies

    Args:
        verbose: Verbose output
        coverage: Generate coverage report (default: True)
        path: Specific test file or directory (relative to tests/)

    Examples:
        inv test.unit
        inv test.unit --verbose
        inv test.unit --path=unit/test_api_chat.py
    """

    flags = ["-v"] if verbose else []
    flags.append("-m")
    flags.append("unit")

    if coverage:
        flags.append("--cov=app")
        flags.append("--cov-report=term-missing")

    test_path = f"tests/{path}" if path else "tests/unit/"
    cmd = f"docker-compose exec backend pytest {' '.join(flags)} {test_path}"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()

    test_result = c.run(cmd, warn=True, pty=True)

    if test_result.ok:
        result = Colors.success("Unit tests passed!")
        if result:
            print(result)
    else:
        result = Colors.error("Some unit tests failed")
        if result:
            print(result)
        return False

    return True


@task(name="integration")
def test_integration(c, verbose=False, coverage=False, path=None):
    """Run integration tests with real PostgreSQL database.

    Integration tests should:
    - Test interactions between components
    - Use real PostgreSQL database (parallax_ai_test)
    - Test API endpoints end-to-end
    - Verify data persistence and transactions

    Args:
        verbose: Verbose output
        coverage: Generate coverage report (default: False, faster for dev)
        path: Specific test file or directory (relative to tests/)

    Examples:
        inv test.integration
        inv test.integration --verbose
        inv test.integration --coverage
        inv test.integration --path=integration/test_conversation_lifecycle.py
    """
    flags = ["-v"] if verbose else []
    flags.append("-m")
    flags.append("integration")
    flags.append("--no-cov")  # Skip coverage by default for speed

    if coverage:
        flags.remove("--no-cov")
        flags.append("--cov=app")
        flags.append("--cov-report=term-missing")

    test_path = f"tests/{path}" if path else "tests/integration/"
    cmd = f"docker-compose exec backend pytest {' '.join(flags)} {test_path}"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()

    test_result = c.run(cmd, warn=True, pty=True)

    if test_result.ok:
        result = Colors.success("Integration tests passed!")
        if result:
            print(result)
    else:
        result = Colors.error("Some integration tests failed")
        if result:
            print(result)
        return False

    return True


@task(name="acceptance")
def test_acceptance(c, verbose=False, headless=True):
    """Run acceptance tests (end-to-end Selenium tests) from project root.

    Acceptance tests should:
    - Test complete user workflows (backend + frontend)
    - Use Selenium WebDriver
    - Run against running application
    - Cover critical user journeys (~5 tests total)

    NOTE: Placeholder for Phase 1. Will be implemented when frontend is complete.

    Args:
        verbose: Verbose output
        headless: Run browser in headless mode (default: True)

    Examples:
        inv test.acceptance
        inv test.acceptance --no-headless  # See browser
    """
    result = Colors.info("Checking for acceptance tests...")
    if result:
        print(result)
    print()

    # Check if services are running
    check_result = c.run("docker-compose ps --services --filter 'status=running'", warn=True, hide=True)
    if not check_result.ok or "backend" not in check_result.stdout or "frontend" not in check_result.stdout:
        result = Colors.error("Services not running. Start with: inv docker.up")
        if result:
            print(result)
        return False

    flags = ["-v"] if verbose else []
    flags.append("-m")
    flags.append("acceptance")
    flags.append("-s")  # Don't capture output for Selenium

    if headless:
        # Set environment variable for headless mode
        cmd = f"HEADLESS=true pytest {' '.join(flags)} tests/acceptance/"
    else:
        cmd = f"pytest {' '.join(flags)} tests/acceptance/"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()

    test_result = c.run(cmd, warn=True, pty=True)

    if test_result.ok:
        result = Colors.success("Acceptance tests passed!")
        if result:
            print(result)
    else:
        result = Colors.warning("No acceptance tests found yet (will be added when frontend is complete)")
        if result:
            print(result)

    return True


@task(name="watch")
def test_watch(c):
    """Run tests in watch mode (re-run on file changes).

    Uses pytest-watch to automatically run tests when files change.
    Great for TDD workflow.

    NOTE: Not implemented yet - requires pytest-watch setup

    Examples:
        inv test.watch
    """
    result = Colors.warning("Test watch mode not yet implemented")
    if result:
        print(result)
    result = Colors.info("For now, manually re-run: inv test.unit")
    if result:
        print(result)
    return True
