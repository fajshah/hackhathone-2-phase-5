# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app

# Set work directory
WORKDIR ${APP_HOME}

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy project requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY backend/src ./src
COPY backend/entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Run the application
ENTRYPOINT ["/entrypoint.sh"]