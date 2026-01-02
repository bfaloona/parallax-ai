"""Frontend (Next.js) development tasks."""

from invoke import task


@task
def shell(c):
    """Open shell in frontend container (Phase 1+).

    Examples:
        inv frontend.shell
    """
    print("→ frontend.shell - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires frontend container running")
    print("")
    container = "parallax-ai-frontend-1"
    cmd = f"docker exec -it {container} /bin/sh"

    print("Expected command:")
    print(f"  {cmd}")
    print("")
    print("For now, use:")
    print("  inv docker.exec-shell --service=frontend")


@task
def test(c, watch=False, coverage=False):
    """Run frontend tests (Phase 1+).

    Args:
        watch: Run in watch mode
        coverage: Generate coverage report

    Examples:
        inv frontend.test
        inv frontend.test --watch
        inv frontend.test --coverage
    """
    print("→ frontend.test - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires test framework setup")
    print("")
    print("This command will:")
    if watch:
        print("  1. Run tests in watch mode")
    else:
        print("  1. Run all frontend tests once")

    if coverage:
        print("  2. Generate coverage report")

    print("")
    print("Expected command:")
    flags = []
    if watch:
        flags.append("--watch")
    if coverage:
        flags.append("--coverage")

    print(f"  docker exec eager-pare-frontend-1 npm test {' '.join(flags)}")


@task
def lint(c, fix=False):
    """Run ESLint and Prettier on frontend code (Phase 1+).

    Args:
        fix: Auto-fix issues where possible

    Examples:
        inv frontend.lint
        inv frontend.lint --fix
    """
    print("→ frontend.lint - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires ESLint/Prettier configuration")
    print("")
    print("This command will:")
    if fix:
        print("  1. Run ESLint with --fix")
        print("  2. Run Prettier with --write")
    else:
        print("  1. Run ESLint (check only)")
        print("  2. Run Prettier (check only)")

    print("")
    print("Expected commands:")
    if fix:
        print("  docker exec eager-pare-frontend-1 npm run lint:fix")
        print("  docker exec eager-pare-frontend-1 npm run format:write")
    else:
        print("  docker exec eager-pare-frontend-1 npm run lint")
        print("  docker exec eager-pare-frontend-1 npm run format:check")


@task
def type_check(c):
    """Run TypeScript type checking (Phase 1+).

    Examples:
        inv frontend.type-check
    """
    print("→ frontend.type-check - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires frontend container running")
    print("")
    print("This command will:")
    print("  1. Run TypeScript compiler in check mode")
    print("  2. Report type errors without building")
    print("")
    print("Expected command:")
    print("  docker exec eager-pare-frontend-1 npm run type-check")


@task
def build(c, production=True):
    """Build frontend for production (Phase 1+).

    Args:
        production: Build for production (default: True)

    Examples:
        inv frontend.build
        inv frontend.build --no-production  # Development build
    """
    print("→ frontend.build - Phase 1+ (Minimal Round Trip)")
    print("⚠️  Not yet implemented - requires frontend container running")
    print("")
    print("This command will:")
    if production:
        print("  1. Run Next.js production build")
        print("  2. Optimize bundles and assets")
    else:
        print("  1. Run Next.js development build")

    print("")
    print("Expected command:")
    cmd = "npm run build" if production else "npm run build:dev"
    print(f"  docker exec eager-pare-frontend-1 {cmd}")


@task
def logs(c, follow=True, tail=100):
    """View frontend container logs.

    Args:
        follow: Follow log output (default: True)
        tail: Number of lines to show (default: 100)

    Examples:
        inv frontend.logs
        inv frontend.logs --no-follow --tail=500
    """
    flags = []
    if follow:
        flags.append("-f")
    if tail:
        flags.append(f"--tail={tail}")

    cmd = f"docker-compose logs {' '.join(flags)} frontend"

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def restart(c):
    """Restart frontend container (Phase 1+).

    Examples:
        inv frontend.restart
    """
    cmd = "docker-compose restart frontend"

    print(f"→ Running: {cmd}")
    c.run(cmd, pty=True)


@task
def analyze(c):
    """Analyze frontend bundle size (Phase 8+).

    Examples:
        inv frontend.analyze
    """
    print("→ frontend.analyze - Phase 8+ (UI Polish)")
    print("⚠️  Not yet implemented - requires bundle analyzer setup")
    print("")
    print("This command will:")
    print("  1. Build with bundle analyzer")
    print("  2. Generate interactive visualization")
    print("  3. Open report in browser")
    print("")
    print("Expected command:")
    print("  docker exec eager-pare-frontend-1 npm run analyze")


@task
def storybook(c, build=False):
    """Run or build Storybook (Phase 8+).

    Args:
        build: Build static Storybook instead of running dev server

    Examples:
        inv frontend.storybook
        inv frontend.storybook --build
    """
    print("→ frontend.storybook - Phase 8+ (UI Polish)")
    print("⚠️  Not yet implemented - requires Storybook setup")
    print("")
    if build:
        print("This command will:")
        print("  1. Build static Storybook site")
        print("  2. Output to storybook-static/")
    else:
        print("This command will:")
        print("  1. Start Storybook dev server")
        print("  2. Open at http://localhost:6006")

    print("")
    print("Expected command:")
    cmd = "npm run storybook:build" if build else "npm run storybook"
    print(f"  docker exec -it eager-pare-frontend-1 {cmd}")
