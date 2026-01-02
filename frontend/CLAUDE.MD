# Claude Instructions for Parallax AI

This document outlines the best practices and coding standards for the Parallax AI project, which utilizes a stack comprising Python, Langflow, Next.js, PostgreSQL, and Docker.

## Project Overview
- **Backend**: Python (FastAPI/Langflow)
- **Frontend**: Next.js
- **Database**: PostgreSQL
- **Infrastructure**: Docker & Docker Compose

## General Guidelines
- **Code Quality**: Write clean, readable, and maintainable code.
- **Documentation**: Document complex logic and all helpful API contract / endpoint details.
- **Type Safety**: Use strict typing in both Python (Type Hints) and TypeScript.
- **Business Logic Placement**: Primary business logic should reside in Python (Backend). Only place logic in TypeScript (Frontend) if it significantly improves simplicity or performance (e.g., immediate UI feedback).
- **Architecture & Critical Thinking**:
    - **Review Implications**: Take extra care to review the architectural implications of all changes.
    - **Clarify**: Ask clarifying questions whenever requirements are ambiguous or could lead to architectural debt.
    - **Push Back**: Proactively push back on requests that suggest non-optimal or anti-pattern solutions.

---

## Python & Langflow Best Practices

### Python
1.  **Type Hinting**: Always use type hints for function arguments and return values.
    ```python
    def process_data(data: dict[str, Any]) -> list[str]:
        ...
    ```
2.  **Pydantic**: Use Pydantic models for data validation and settings management, especially for API request/response bodies.
3.  **Async/Await**: Utilize `async` and `await` for I/O bound operations, particularly database queries and external API calls.
4.  **Error Handling**: Use specific exception handling rather than bare `except:` blocks.
5.  **Linting/Formatting**: Follow PEP 8 standards. Use `black` and `isort` for formatting.

### Langflow
1.  **Custom Components**: When creating custom components for Langflow:
    - Inherit from the base `CustomComponent` class.
    - Define clear inputs and outputs with type annotations.
    - Handle errors gracefully within the `build` method to prevent crashing the flow.
2.  **Flow Management**:
    - Keep flows modular. Break down complex flows into sub-flows if possible.
    - Export and version control your JSON flow definitions.

---

## Next.js (Frontend) Best Practices

1.  **App Router**: Use the Next.js App Router (`app/` directory) structure.
2.  **TypeScript**: Use TypeScript for all components and utilities. Avoid `any` types.
3.  **Server vs. Client Components**:
    - Default to **Server Components** for data fetching and static rendering.
    - Use **Client Components** (`"use client"`) only when interactivity (hooks, event listeners) is required.
4.  **Data Fetching**:
    - Fetch data directly in Server Components where possible.
    - Use `SWR` or `TanStack Query` for client-side data fetching and caching.
5.  **UI/UX**:
    - Use Tailwind CSS for styling.
    - Ensure responsive design for all components.

---

## PostgreSQL Best Practices

1.  **ORM Usage**:
    - If using Python backend: Use **SQLAlchemy** (async) or **SQLModel**.
    - If connecting directly from Next.js (less common in this stack if Python is the main backend): Use **Prisma**.
2.  **Migrations**: Always use migration tools (e.g., `alembic` for Python) to manage database schema changes. Never modify the schema manually in production.
3.  **Indexing**: Add indexes to columns that are frequently queried or used in join conditions.
4.  **Environment Variables**: Store database credentials in `.env` files and never commit them to version control.

---

## Docker & Infrastructure

1.  **Docker Compose**:
    - Use `docker-compose.yml` to orchestrate services (Frontend, Backend, DB, Langflow).
    - Define health checks for dependent services (e.g., wait for Postgres to be ready before starting the backend).
2.  **Multi-Stage Builds**: Use multi-stage Dockerfiles to keep production image sizes small.
    - *Example*: Build frontend assets in a node image, then copy static files to a lightweight nginx or node runner image.
3.  **Volumes**: Use named volumes for database persistence so data isn't lost when containers are recreated.
4.  **Networking**: Use internal Docker networks for communication between services. Do not expose database ports to the host unless necessary for debugging.

## Workflow

1.  **Development**:
    - Run `docker-compose up` to start the development environment.
    - Changes in code should trigger hot-reloads (configure volumes correctly for this).
2.  **Testing**: Write unit tests for Python logic (pytest) and frontend components (Jest/React Testing Library).
