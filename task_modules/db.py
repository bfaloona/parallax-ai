"""Database management tasks."""

from invoke import task
from datetime import datetime
from task_modules import Colors


@task
def shell(c):
    """Connect to PostgreSQL shell.

    Examples:
        inv db.shell
    """
    cmd = "docker-compose exec postgres psql -U parallax -d parallax_ai"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
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
        result = Colors.warning("This will DELETE ALL DATABASE DATA.")
        if result:
            print(result)
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            result = Colors.info("Aborted")
            if result:
                print(result)
            return

    result = Colors.command(" docker-compose down -v")
    if result:
        print(result)
    print()
    c.run("docker-compose down -v", pty=True)

    result = Colors.command(" docker-compose up -d postgres")
    if result:
        print(result)
    print()
    c.run("docker-compose up -d postgres", pty=True)

    result = Colors.success("Database reset complete. Waiting for health check...")
    if result:
        print(result)
    c.run("sleep 5", pty=True)

    cmd = "docker-compose exec postgres psql -U parallax -d parallax_ai -c '\\l'"
    result = Colors.command(cmd)
    if result:
        print(result)
    print()
    verify_result = c.run(cmd, pty=True, warn=True)

    if verify_result.ok:
        result = Colors.success("Database verified and ready")
        if result:
            print(result)
    else:
        result = Colors.warning("Database may still be initializing. Try 'inv db.shell' in a few seconds.")
        if result:
            print(result)


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

    cmd = f"docker-compose exec -T postgres pg_dump -U parallax parallax_ai > {filename}"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
    c.run(cmd, pty=True)

    result = Colors.success(f"Database backed up to: {filename}")
    if result:
        print(result)


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
        result = Colors.warning(f"This will REPLACE ALL DATA with {filename}.")
        if result:
            print(result)
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            result = Colors.info("Aborted")
            if result:
                print(result)
            return

    # First, reset the database
    result = Colors.info("Resetting database...")
    if result:
        print(result)
    reset(c, confirm=False)

    # Restore from file
    cmd = f"docker-compose exec -T postgres psql -U parallax parallax_ai < {filename}"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
    c.run(cmd, pty=True)

    result = Colors.success(f"Database restored from: {filename}")
    if result:
        print(result)


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
    result = Colors.info("Checking container status...")
    if result:
        print(result)

    # Check if postgres service is running
    check_result = c.run("docker-compose ps postgres", warn=True, hide=True)

    if not check_result.ok or "Up" not in check_result.stdout:
        result = Colors.error("PostgreSQL container is not running")
        if result:
            print(result)
        print("  Start with: inv docker.up --service=postgres")
        return

    result = Colors.success("PostgreSQL container is running")
    if result:
        print(result)

    print()
    result = Colors.info("Checking database connection...")
    if result:
        print(result)

    cmd = "docker-compose exec -T postgres psql -U parallax -d parallax_ai -c '\\l'"
    db_result = c.run(cmd, warn=True, hide=True)

    if db_result.ok:
        result = Colors.success("Database 'parallax_ai' is accessible")
        if result:
            print(result)

        # Show table count
        cmd = "docker-compose exec -T postgres psql -U parallax -d parallax_ai -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'\""
        count_result = c.run(cmd, warn=True, hide=True)
        if count_result.ok:
            table_count = count_result.stdout.strip()
            print(f"  Tables: {table_count}")
    else:
        result = Colors.error("Cannot connect to database")
        if result:
            print(result)
        print("  Database may still be initializing. Try again in a few seconds.")
