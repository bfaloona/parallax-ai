"""Database management tasks."""

from invoke import task
from datetime import datetime


@task
def shell(c):
    """Connect to PostgreSQL shell.

    Examples:
        inv db.shell
    """
    container = "eager-pare-postgres-1"
    cmd = f"docker exec -it {container} psql -U parallax -d parallax_ai"

    print(f"→ Running: docker exec -it {container} psql -U parallax -d parallax_ai")
    c.run(cmd, pty=True)


@task
def reset(c, confirm=True):
    """Reset database by removing volume and recreating (DESTRUCTIVE).

    Args:
        confirm: Require confirmation (default: True)

    Examples:
        inv db.reset
        inv db.reset --no-confirm  # Skip confirmation
    """
    if confirm:
        response = input("⚠️  This will DELETE ALL DATABASE DATA. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    print("→ Running: docker-compose down -v")
    c.run("docker-compose down -v", pty=True)

    print("→ Running: docker-compose up -d postgres")
    c.run("docker-compose up -d postgres", pty=True)

    print("✓ Database reset complete. Waiting for health check...")
    c.run("sleep 5", pty=True)

    print("→ Running: docker exec eager-pare-postgres-1 psql -U parallax -d parallax_ai -c '\\l'")
    result = c.run(
        "docker exec eager-pare-postgres-1 psql -U parallax -d parallax_ai -c '\\l'",
        pty=True,
        warn=True
    )

    if result.ok:
        print("✓ Database verified and ready")
    else:
        print("⚠️  Database may still be initializing. Try 'inv db.shell' in a few seconds.")


@task
def backup(c, filename=None):
    """Backup database to SQL file.

    Args:
        filename: Output filename (default: backup_YYYYMMDD_HHMMSS.sql)

    Examples:
        inv db.backup
        inv db.backup --filename=my_backup.sql
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.sql"

    container = "eager-pare-postgres-1"
    cmd = f"docker exec {container} pg_dump -U parallax parallax_ai > {filename}"

    print(f"→ Running: docker exec {container} pg_dump -U parallax parallax_ai > {filename}")
    c.run(cmd, pty=True)
    print(f"✓ Database backed up to: {filename}")


@task
def restore(c, filename, confirm=True):
    """Restore database from SQL file (DESTRUCTIVE).

    Args:
        filename: SQL file to restore from
        confirm: Require confirmation (default: True)

    Examples:
        inv db.restore --filename=backup_20260102_120000.sql
    """
    if confirm:
        response = input(f"⚠️  This will REPLACE ALL DATA with {filename}. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    container = "eager-pare-postgres-1"

    # First, reset the database
    print("→ Resetting database...")
    reset(c, confirm=False)

    # Restore from file
    cmd = f"docker exec -i {container} psql -U parallax parallax_ai < {filename}"

    print(f"→ Running: docker exec -i {container} psql -U parallax parallax_ai < {filename}")
    c.run(cmd, pty=True)
    print(f"✓ Database restored from: {filename}")


@task
def init(c):
    """Initialize database schema (Phase 2+).

    This will run Alembic migrations to set up the database schema.
    Currently a stub - will be implemented in Phase 2.

    Examples:
        inv db.init
    """
    print("→ db.init - Phase 2+ (Database & Auth)")
    print("⚠️  Not yet implemented - requires Alembic migrations from Phase 2")
    print("")
    print("This command will:")
    print("  1. Run Alembic migrations to create tables")
    print("  2. Set up initial database schema")
    print("  3. Optionally create a test user")
    print("")
    print("See: docs/MIGRATION_GUIDE.md Phase 2 for implementation details")


@task
def migrate(c, message=None):
    """Run database migrations (Phase 2+).

    Args:
        message: Migration message (for auto-generating migrations)

    Examples:
        inv db.migrate
        inv db.migrate --message="add user table"
    """
    print("→ db.migrate - Phase 2+ (Database & Auth)")
    print("⚠️  Not yet implemented - requires Alembic setup from Phase 2")
    print("")
    print("This command will:")
    if message:
        print(f"  1. Auto-generate migration: {message}")
        print("  2. Review the generated migration file")
    else:
        print("  1. Run pending migrations")
        print("  2. Update database schema to latest version")
    print("")
    print("See: docs/MIGRATION_GUIDE.md Phase 2 for implementation details")


@task
def status(c):
    """Show database connection status and basic info.

    Examples:
        inv db.status
    """
    container = "eager-pare-postgres-1"

    print("→ Checking container status...")
    result = c.run(f"docker ps | grep {container}", warn=True, hide=True)

    if not result.ok:
        print(f"✗ Container '{container}' is not running")
        print("  Start with: inv docker.up --service=postgres")
        return

    print(f"✓ Container '{container}' is running")

    print("\n→ Checking database connection...")
    cmd = f"docker exec {container} psql -U parallax -d parallax_ai -c '\\l'"
    result = c.run(cmd, warn=True, hide=True)

    if result.ok:
        print("✓ Database 'parallax_ai' is accessible")

        # Show table count
        cmd = f"docker exec {container} psql -U parallax -d parallax_ai -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'\""
        result = c.run(cmd, warn=True, hide=True)
        if result.ok:
            table_count = result.stdout.strip()
            print(f"  Tables: {table_count}")
    else:
        print("✗ Cannot connect to database")
        print("  Database may still be initializing. Try again in a few seconds.")
