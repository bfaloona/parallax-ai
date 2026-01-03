"""Docker and infrastructure management tasks."""

from invoke import task
from task_modules import Colors


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

    result = Colors.command(cmd)
    if result:  # Print if not using Rich (Rich prints directly)
        print(result)
    print()  # Blank line for separation
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
        result = Colors.warning("This will delete all database data!")
        if result:
            print(result)
    if remove_orphans:
        flags.append("--remove-orphans")

    cmd = f"docker-compose down {' '.join(flags)}".strip()

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
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

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
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

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
    c.run(cmd, pty=True)


@task
def ps(c):
    """List running containers.

    Examples:
        inv docker.ps
    """
    cmd = "docker-compose ps"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
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

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
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
        result = Colors.warning("This will DELETE ALL DATA and containers.")
        if result:
            print(result)
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            result = Colors.info("Aborted")
            if result:
                print(result)
            return

    cmd = "docker-compose down -v --remove-orphans"

    result = Colors.command(cmd)
    if result:
        print(result)
    print()
    c.run(cmd, pty=True)
    result = Colors.success("Cleanup complete")
    if result:
        print(result)


@task
def info(c):
    """Show Docker system status with formatted tables.

    Displays:
    - Running containers with status and ports
    - Docker images (top 10 by size)
    - Disk usage summary with reclaimable space
    - Quick action commands

    Examples:
        inv docker.info
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        import json

        console = Console()

        # 1. Running Containers
        result = c.run("docker ps --format '{{json .}}'", hide=True, warn=True)
        if result.ok and result.stdout.strip():
            containers_table = Table(title="🐳 Running Containers", show_header=True, header_style="bold cyan")
            containers_table.add_column("Name", style="cyan", no_wrap=True)
            containers_table.add_column("Status", style="green")
            containers_table.add_column("Ports", style="yellow")

            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    containers_table.add_row(
                        container['Names'],
                        container['Status'],
                        container.get('Ports', '-')
                    )

            console.print(containers_table)
            console.print()
        else:
            console.print("[yellow]No running containers[/yellow]\n")

        # 2. Docker Images (Top 10)
        result = c.run("docker images --format '{{json .}}'", hide=True, warn=True)
        if result.ok and result.stdout.strip():
            images_table = Table(title="📦 Docker Images (Top 10 by size)", show_header=True, header_style="bold cyan")
            images_table.add_column("Repository", style="cyan")
            images_table.add_column("Tag", style="yellow")
            images_table.add_column("Size", style="magenta", justify="right")

            lines = result.stdout.strip().split('\n')[:10]
            for line in lines:
                if line:
                    img = json.loads(line)
                    images_table.add_row(
                        img['Repository'][:40],
                        img['Tag'][:20],
                        img['Size']
                    )

            console.print(images_table)
            console.print()

        # 3. Disk Usage
        result = c.run("docker system df", hide=True, warn=True)
        if result.ok:
            console.print("[bold cyan]💾 Disk Usage[/bold cyan]")
            console.print(result.stdout)
            console.print()

        # 4. Quick Actions Panel
        actions = Panel(
            "[cyan]inv docker.clean[/cyan]        - Remove unused containers, images, and volumes\n"
            "[cyan]inv docker.ps[/cyan]           - List all containers (running and stopped)\n"
            "[cyan]inv docker.logs --service=X[/cyan] - View logs for a specific service\n"
            "[cyan]inv docker.up[/cyan]           - Start all services\n"
            "[cyan]inv docker.down[/cyan]         - Stop all services",
            title="💡 Quick Actions",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(actions)

    except ImportError:
        # Fallback to simple output if Rich not available
        result = Colors.cmd("Docker System Information")
        if result:
            print(result)
        print("=" * 60)

        print(f"\n{Colors.BOLD}Running Containers:{Colors.END}")
        c.run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", pty=True)

        print(f"\n{Colors.BOLD}Docker Images (Top 10):{Colors.END}")
        c.run("docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}' | head -11", pty=True)

        print(f"\n{Colors.BOLD}Disk Usage:{Colors.END}")
        c.run("docker system df", pty=True)

        print(f"\n{Colors.BOLD}Quick Actions:{Colors.END}")
        print("  inv docker.clean        - Remove unused data")
        print("  inv docker.ps           - List containers")
        print("  inv docker.logs --service=X - View logs")


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
    user_flag = f"-u {user}" if user else ""
    cmd = f"docker-compose exec {user_flag} {service} /bin/sh".strip()

    result = Colors.cmd(f"Opening shell in {service} container")
    if result:
        print(result)
    print()
    c.run(cmd, pty=True)
