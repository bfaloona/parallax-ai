"""Docker and infrastructure management tasks."""

from invoke import task


@task
def up(c, detach=True, service=None):
    """Start all services (or specific service).

    Args:
        detach: Run in detached mode (default: True)
        service: Specific service to start (optional)

    Examples:
        inv docker.up
        inv docker.up --no-detach
        inv docker.up --service=postgres
    """
    flag = "-d" if detach else ""
    service_arg = service if service else ""
    cmd = f"docker-compose up {flag} {service_arg}".strip()

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def down(c, volumes=False, remove_orphans=True):
    """Stop all services.

    Args:
        volumes: Remove volumes (WARNING: deletes data)
        remove_orphans: Remove containers for services not in docker-compose.yml

    Examples:
        inv docker.down
        inv docker.down --volumes  # WARNING: destroys data
    """
    flags = []
    if volumes:
        flags.append("-v")
        print("⚠️  WARNING: This will delete all database data!")
    if remove_orphans:
        flags.append("--remove-orphans")

    cmd = f"docker-compose down {' '.join(flags)}".strip()

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def restart(c, service=None):
    """Restart services (or specific service).

    Args:
        service: Specific service to restart (optional)

    Examples:
        inv docker.restart
        inv docker.restart --service=backend
    """
    service_arg = service if service else ""
    cmd = f"docker-compose restart {service_arg}".strip()

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def logs(c, service=None, follow=True, tail=100):
    """View service logs.

    Args:
        service: Specific service (default: all services)
        follow: Follow log output (default: True)
        tail: Number of lines to show from end (default: 100)

    Examples:
        inv docker.logs
        inv docker.logs --service=postgres
        inv docker.logs --service=backend --tail=500
        inv docker.logs --no-follow
    """
    flags = []
    if follow:
        flags.append("-f")
    if tail:
        flags.append(f"--tail={tail}")

    service_arg = service if service else ""
    cmd = f"docker-compose logs {' '.join(flags)} {service_arg}".strip()

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def ps(c):
    """List running containers.

    Examples:
        inv docker.ps
    """
    cmd = "docker-compose ps"

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def build(c, service=None, no_cache=False):
    """Build or rebuild services.

    Args:
        service: Specific service to build (optional)
        no_cache: Don't use cache when building

    Examples:
        inv docker.build
        inv docker.build --service=backend
        inv docker.build --no-cache
    """
    flags = []
    if no_cache:
        flags.append("--no-cache")

    service_arg = service if service else ""
    cmd = f"docker-compose build {' '.join(flags)} {service_arg}".strip()

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def clean(c, confirm=True):
    """Remove all containers, volumes, and orphans (DESTRUCTIVE).

    Args:
        confirm: Require confirmation (default: True)

    Examples:
        inv docker.clean
        inv docker.clean --no-confirm  # Skip confirmation
    """
    if confirm:
        response = input("⚠️  This will DELETE ALL DATA and containers. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    cmd = "docker-compose down -v --remove-orphans"

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)
    print("✓ Cleanup complete")


@task
def exec_shell(c, service, user=None):
    """Execute a shell in a running container.

    Args:
        service: Service name (postgres, backend, frontend)
        user: User to run as (optional)

    Examples:
        inv docker.exec-shell --service=backend
        inv docker.exec-shell --service=postgres --user=postgres
    """
    container_name = f"parallax-ai-{service}-1"
    user_flag = f"-u {user}" if user else ""
    cmd = f"docker exec -it {user_flag} {container_name} /bin/sh"

    print(f"→ Running: docker exec -it {container_name} /bin/sh")
    c.run(cmd, pty=True)
