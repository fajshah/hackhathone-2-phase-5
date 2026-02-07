@echo off
REM Script to build Docker images for Phase 5 Todo AI Chatbot

echo Building Phase 5 Todo AI Chatbot Docker Images...

echo.
echo Building Backend Image...
docker build -f Dockerfile.backend -t todo-backend:phase5 .

echo.
echo Building Frontend Image...
docker build -f Dockerfile.frontend -t todo-frontend:phase5 .

echo.
echo Built Images:
docker images | findstr "todo-"

echo.
echo Build process completed!
echo To run the application, use: docker-compose -f docker-compose.phase5.yaml up