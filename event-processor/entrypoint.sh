#!/bin/sh

echo "Starting event processor service..."

# Run the application
exec python -c "from src.consumers.task_consumer import run_task_event_consumer; import asyncio; asyncio.run(run_task_event_consumer())"