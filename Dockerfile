# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VENV_PATH="/opt/poetry-venv"

# Install Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gcc git \
    && curl -sSL 'https://install.python-poetry.org' | python - \
    && poetry --version \
    && apt-get remove -y curl gcc git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy project requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]