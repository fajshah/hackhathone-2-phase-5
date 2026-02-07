# Phase 5 Docker Images Build Guide

## Building the Docker Images

### Windows:
```cmd
# Make the script executable
chmod +x build-images.bat

# Run the build script
build-images.bat
```

### Linux/Mac:
```bash
# Make the script executable
chmod +x build-images.sh

# Run the build script
./build-images.sh
```

### Manual Build Commands:
```bash
# Build Backend
docker build -f Dockerfile.backend -t todo-backend:phase5 .

# Build Frontend
docker build -f Dockerfile.frontend -t todo-frontend:phase5 .
```

## Running the Application

```bash
# Start the full application stack
docker-compose -f docker-compose.phase5.yaml up

# Or start individual services
docker run -d -p 8000:8000 todo-backend:phase5
docker run -d -p 3000:80 todo-frontend:phase5
```

## Image Details

### Backend Image (todo-backend:phase5)
- Based on Python 3.11-slim
- Includes all necessary Python dependencies
- Runs the FastAPI application
- Exposes port 8000
- Includes authentication system and JWT handling

### Frontend Image (todo-frontend:phase5)
- Based on Node.js 18-alpine for build
- Uses Nginx for production serving
- Optimized build with minimized assets
- Exposes port 80
- Includes React application with authentication flow

## Docker Compose Services
- **postgres**: PostgreSQL database for persistent storage
- **backend**: FastAPI application with authentication
- **frontend**: React application with Nginx server
- All services are properly linked and configured for production use