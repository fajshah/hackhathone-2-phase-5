# Docker Setup Instructions

This project uses Docker to containerize the application and its dependencies.

## Prerequisites

- Docker Desktop installed on your machine
- Docker Compose (usually included with Docker Desktop)

## Quick Start

1. Make sure you have Docker running on your machine.

2. Navigate to the project directory:
   ```bash
   cd D:\phase-5
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the application at `http://localhost:5000`

## Available Services

- **Backend API**: Runs on port 5000
- **PostgreSQL Database**: Runs on port 5432
- **Redis**: Runs on port 6379

## Useful Commands

- Start services in detached mode: `docker-compose up -d`
- Stop services: `docker-compose down`
- View logs: `docker-compose logs -f`
- Run commands in a service: `docker-compose exec backend bash`
- Rebuild containers: `docker-compose up --build`

## Environment Variables

Make sure your `.env` file is properly configured before starting the containers.

## Troubleshooting

- If you get permission errors, make sure Docker Desktop is running with appropriate permissions.
- If the database fails to connect, wait a moment for PostgreSQL to fully initialize.
- Check logs with `docker-compose logs` to diagnose issues.