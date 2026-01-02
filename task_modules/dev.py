"""Development workflow tasks."""

from invoke import task
import os
import secrets


@task
def setup(c):
    """Initial project setup for new developers.

    This command:
    1. Checks all prerequisites
    2. Generates secrets if needed
    3. Sets up .env file
    4. Installs dependencies
    5. Starts services

    Examples:
        inv dev.setup
    """
    print("=== Parallax AI Development Setup ===\n")

    # Check prerequisites
    print("→ Step 1: Checking prerequisites...")
    check(c)

    # Check for .env file
    print("\n→ Step 2: Checking environment configuration...")
    if not os.path.exists(".env"):
        print("  .env file not found. Creating from .env.example...")
        c.run("cp .env.example .env", pty=True)
        print("  ✓ Created .env file")
        print("\n  ⚠️  IMPORTANT: Edit .env and add:")
        print("     - ANTHROPIC_API_KEY (required for Phase 1+)")
        print("     - JWT_SECRET (generate with: inv dev.secrets)")
    else:
        print("  ✓ .env file exists")

    # Install Python dev dependencies
    print("\n→ Step 3: Installing Python development dependencies...")
    cmd = "pip install -r requirements-dev.txt"
    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)

    # Start services
    print("\n→ Step 4: Starting PostgreSQL...")
    c.run("docker-compose up -d postgres", pty=True)

    print("\n✓ Setup complete!")
    print("\nNext steps:")
    print("  1. Edit .env file with your API keys")
    print("  2. Run 'inv dev.check' to verify everything is working")
    print("  3. See 'inv --list' for all available commands")
    print("  4. See docs/DEVELOPER_COMMANDS.md for detailed documentation")


@task
def check(c):
    """Verify all development prerequisites are installed.

    Examples:
        inv dev.check
    """
    print("Checking development prerequisites...\n")

    checks = [
        ("docker --version", "Docker"),
        ("docker-compose --version", "Docker Compose"),
        ("node --version", "Node.js"),
        ("python3 --version", "Python"),
        ("git --version", "Git"),
    ]

    all_ok = True
    for cmd, name in checks:
        result = c.run(cmd, warn=True, hide=True)
        if result.ok:
            version = result.stdout.strip().split('\n')[0]
            print(f"✓ {name:20} {version}")
        else:
            print(f"✗ {name:20} NOT FOUND")
            all_ok = False

    # Check for .env file
    if os.path.exists(".env"):
        print(f"✓ {'.env file':20} Found")

        # Check for critical env vars
        with open(".env") as f:
            env_content = f.read()
            if "sk-ant-api03-" in env_content and len(env_content.split("sk-ant-api03-")[1].split()[0]) > 20:
                print(f"✓ {'ANTHROPIC_API_KEY':20} Configured")
            else:
                print(f"⚠️  {'ANTHROPIC_API_KEY':20} Not set (required for Phase 1+)")

            if "JWT_SECRET" in env_content and "your-256-bit-secret" not in env_content:
                print(f"✓ {'JWT_SECRET':20} Configured")
            else:
                print(f"⚠️  {'JWT_SECRET':20} Not set (generate with: inv dev.secrets)")
    else:
        print(f"✗ {'.env file':20} NOT FOUND (run: inv dev.setup)")
        all_ok = False

    # Check Docker containers
    print()
    result = c.run("docker ps --format '{{.Names}}' | grep eager-pare", warn=True, hide=True)
    if result.ok:
        containers = result.stdout.strip().split('\n')
        for container in containers:
            print(f"✓ {'Container':20} {container}")
    else:
        print(f"⚠️  {'Containers':20} None running (run: inv docker.up)")

    print()
    if all_ok:
        print("✓ All checks passed!")
    else:
        print("⚠️  Some checks failed. Run 'inv dev.setup' to fix.")

    return all_ok


@task
def secrets(c, update_env=False):
    """Generate secure secrets for JWT and other auth needs.

    Args:
        update_env: Automatically update .env file (default: False)

    Examples:
        inv dev.secrets
        inv dev.secrets --update-env  # Auto-update .env
    """
    print("Generating secure secrets...\n")

    jwt_secret = secrets.token_hex(32)
    nextauth_secret = secrets.token_hex(32)

    print("JWT_SECRET (256-bit):")
    print(f"  {jwt_secret}")
    print()
    print("NEXTAUTH_SECRET:")
    print(f"  {nextauth_secret}")
    print()

    if update_env and os.path.exists(".env"):
        print("→ Updating .env file...")

        with open(".env", "r") as f:
            content = f.read()

        # Update JWT_SECRET
        if "JWT_SECRET=" in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("JWT_SECRET="):
                    new_lines.append(f"JWT_SECRET={jwt_secret}")
                elif line.startswith("NEXTAUTH_SECRET="):
                    new_lines.append(f"NEXTAUTH_SECRET={nextauth_secret}")
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)

            with open(".env", "w") as f:
                f.write(content)

            print("✓ .env file updated with new secrets")
        else:
            print("⚠️  .env file doesn't have JWT_SECRET entry. Manual update required.")
    else:
        print("To use these secrets:")
        print("  1. Copy the values above")
        print("  2. Edit .env file")
        print("  3. Replace the placeholder values")
        print()
        print("Or run: inv dev.secrets --update-env")


@task
def test(c):
    """Run all tests (Phase 1+).

    This will run both backend and frontend tests.
    Currently a stub - will be implemented in Phase 1+.

    Examples:
        inv dev.test
    """
    print("→ dev.test - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented")
    print("")
    print("This command will:")
    print("  1. Run backend tests (pytest)")
    print("  2. Run frontend tests (Jest/Vitest)")
    print("  3. Show coverage reports")
    print("")
    print("Individual test commands:")
    print("  inv backend.test")
    print("  inv frontend.test")


@task
def lint(c, fix=False):
    """Run linters on all code (Phase 1+).

    Args:
        fix: Auto-fix issues where possible

    Examples:
        inv dev.lint
        inv dev.lint --fix
    """
    print("→ dev.lint - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented")
    print("")
    print("This command will:")
    if fix:
        print("  1. Run black (Python formatter) with --fix")
        print("  2. Run flake8 (Python linter)")
        print("  3. Run ESLint (TypeScript/React) with --fix")
        print("  4. Run Prettier (TypeScript/React) with --write")
    else:
        print("  1. Run black (Python formatter)")
        print("  2. Run flake8 (Python linter)")
        print("  3. Run ESLint (TypeScript/React)")
        print("  4. Run Prettier (TypeScript/React)")
    print("")
    print("Individual lint commands:")
    print("  inv backend.lint")
    print("  inv frontend.lint")


@task
def clean(c):
    """Clean up generated files, caches, and temp data.

    Examples:
        inv dev.clean
    """
    print("→ Cleaning up development artifacts...")

    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/.pytest_cache",
        "**/.mypy_cache",
        "**/node_modules/.cache",
        "**/.next",
    ]

    for pattern in patterns:
        print(f"  Removing: {pattern}")
        c.run(f"find . -type d -name '{pattern.split('/')[-1]}' -exec rm -rf {{}} + 2>/dev/null || true", warn=True)

    print("✓ Cleanup complete")
