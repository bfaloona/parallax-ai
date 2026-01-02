# Parallax AI

Parallax AI is a full-stack application leveraging **FastAPI**, **Next.js**, **Langflow**, and **PostgreSQL**.

## 🏗 Architecture

- **Frontend**: Next.js (React, TypeScript, Tailwind CSS) - Port `3000`
- **Backend**: FastAPI (Python) - Port `8000`
- **Orchestration**: Langflow - Port `7860`
- **Database**: PostgreSQL - Port `5432`

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js (v18+)
- Python (v3.11+)

### Local Development Setup

1.  **Run the setup script**:
    This script creates your `.env` file and installs local dependencies for both Python and Node.js (useful for IDE intellisense).
    ```bash
    ./setup_dev.sh
    ```

2.  **Start the application**:
    Use Docker Compose to spin up all services.
    ```bash
    docker-compose up --build
    ```

3.  **Access the services**:
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API: [http://localhost:8000](http://localhost:8000)
    - Langflow UI: [http://localhost:7860](http://localhost:7860)

## ☁️ Deployment (Coolify)

This project is designed to be deployed on a **Coolify** managed server.

1.  **Create a new Resource** in Coolify.
2.  Select **Git Repository** (Public or Private).
3.  Connect this repository.
4.  **Build Pack**: Select **Docker Compose**.
5.  **Configuration**:
    - Ensure the `docker-compose.yml` is selected.
    - **Environment Variables**: Copy the contents of `.env.example` into the Coolify Environment Variables section.
    - **Important**: Update `NEXT_PUBLIC_API_URL` to point to your production Backend URL (e.g., `https://api.parallax.yourdomain.com`).
    - **Domains**: Configure domains for:
        - Frontend (e.g., `app.parallax.yourdomain.com`) -> Port `3000`
        - Backend (e.g., `api.parallax.yourdomain.com`) -> Port `8000`
        - Langflow (e.g., `flow.parallax.yourdomain.com`) -> Port `7860`

## 📂 Project Structure

```
├── backend/            # FastAPI Application
├── frontend/           # Next.js Application
├── docker-compose.yml  # Service Orchestration
├── setup_dev.sh        # Development Setup Script
└── .env.example        # Environment Variable Template
```
