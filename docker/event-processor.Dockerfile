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

# Copy project requirements (assuming same as backend for now)
RUN pip install --upgrade pip
RUN pip install aiokafka

# Create a basic requirements.txt for the event processor
RUN echo "aiokafka==0.8.0\nasyncio==3.4.3" > requirements.txt
RUN pip install -r requirements.txt

# Copy project
COPY event-processor/src ./src
COPY event-processor/entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose port if needed (though processors usually don't serve HTTP)
EXPOSE 8001

# Run the application
ENTRYPOINT ["/entrypoint.sh"]