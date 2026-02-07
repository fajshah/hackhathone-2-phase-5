"""
Task Events Kafka Consumer for the todo chatbot system.
Consumes task-related events from the task-events topic.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from ..processors.event_processor import EventProcessor


class TaskEventConsumer:
    """
    Consumer for the task-events Kafka topic
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092",
                 group_id: str = "task-events-consumer-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Event processor to handle events
        self.event_processor = None

    async def connect(self):
        """
        Initialize and connect the Kafka consumer for task-events
        """
        self.consumer = AIOKafkaConsumer(
            'task-events',  # Subscribe to task-events topic
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',  # Start from the beginning of the topic
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
        )

        await self.consumer.start()
        self.logger.info(f"Task Event Consumer connected to Kafka at {self.bootstrap_servers}")

        # Initialize event processor to handle events
        self.event_processor = await EventProcessor().connect()

    async def disconnect(self):
        """
        Disconnect and close the Kafka consumer
        """
        if self.consumer:
            await self.consumer.stop()
            self.logger.info("Task Event Consumer disconnected from Kafka")

    async def process_task_event(self, event_data: Dict[str, Any]):
        """
        Process a task-related event from the task-events topic

        Args:
            event_data: The event data to process
        """
        try:
            event_type = event_data.get('event_type', 'unknown')

            self.logger.info(f"Processing task event: {event_type}, ID: {event_data.get('id', 'unknown')}")

            # Handle different task event types
            if event_type == 'task.created':
                await self._handle_task_created(event_data)
            elif event_type == 'task.updated':
                await self._handle_task_updated(event_data)
            elif event_type == 'task.deleted':
                await self._handle_task_deleted(event_data)
            elif event_type == 'task.completed':
                await self._handle_task_completed(event_data)
            elif event_type == 'task.assigned':
                await self._handle_task_assigned(event_data)
            else:
                self.logger.warning(f"Unknown task event type: {event_type}")

        except Exception as e:
            self.logger.error(f"Error processing task event {event_data.get('event_type', 'unknown')}: {str(e)}")
            # In a real implementation, you might send this to a dead-letter queue
            raise

    async def _handle_task_created(self, event_data: Dict[str, Any]):
        """
        Handle a task created event

        Args:
            event_data: The task created event data
        """
        task_data = event_data.get('payload', {}).get('task', {})

        self.logger.info(f"Handling task created event for task: {task_data.get('id')}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Trigger any related workflows
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task created: {task_data.get('title', 'Unknown task')} (ID: {task_data.get('id')})")

    async def _handle_task_updated(self, event_data: Dict[str, Any]):
        """
        Handle a task updated event

        Args:
            event_data: The task updated event data
        """
        task_data = event_data.get('payload', {}).get('task', {})

        self.logger.info(f"Handling task updated event for task: {task_data.get('id')}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Trigger any related workflows
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task updated: {task_data.get('title', 'Unknown task')} (ID: {task_data.get('id')})")

    async def _handle_task_deleted(self, event_data: Dict[str, Any]):
        """
        Handle a task deleted event

        Args:
            event_data: The task deleted event data
        """
        task_data = event_data.get('payload', {}).get('task', {})

        self.logger.info(f"Handling task deleted event for task: {task_data.get('id')}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Trigger any related cleanup workflows
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task deleted: {task_data.get('title', 'Unknown task')} (ID: {task_data.get('id')})")

    async def _handle_task_completed(self, event_data: Dict[str, Any]):
        """
        Handle a task completed event

        Args:
            event_data: The task completed event data
        """
        task_data = event_data.get('payload', {}).get('task', {})

        self.logger.info(f"Handling task completed event for task: {task_data.get('id')}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Trigger any related workflows (e.g., notify dependent tasks)
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task completed: {task_data.get('title', 'Unknown task')} (ID: {task_data.get('id')})")

    async def _handle_task_assigned(self, event_data: Dict[str, Any]):
        """
        Handle a task assigned event

        Args:
            event_data: The task assigned event data
        """
        task_data = event_data.get('payload', {}).get('task', {})

        self.logger.info(f"Handling task assigned event for task: {task_data.get('id')}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Trigger any related workflows (e.g., notify assignee)
        # - Update metrics or analytics systems

        # Example: Log the event
        assigned_to = task_data.get('assigned_to', 'Unassigned')
        print(f"Task assigned: {task_data.get('title', 'Unknown task')} to {assigned_to} (ID: {task_data.get('id')})")

    async def consume_events(self):
        """
        Main consumption loop for task-events topic
        """
        if not self.consumer:
            await self.connect()

        self.is_running = True
        self.logger.info("Starting task event consumption loop...")

        try:
            while self.is_running:
                # Consume messages from the task-events topic
                msg = await self.consumer.getone()

                if msg:
                    try:
                        # Process the task event
                        event_data = msg.value
                        await self.process_task_event(event_data)

                        # Commit the offset after processing
                        await self.consumer.commit()

                    except Exception as e:
                        self.logger.error(f"Error processing task event from {msg.topic}:{msg.partition}@{msg.offset}: {str(e)}")
                        # Don't commit the offset on error so the message can be retried
                        continue
                else:
                    # Small delay to prevent busy-waiting
                    await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Error in task event consumption loop: {str(e)}")
        finally:
            await self.disconnect()

    async def start_listening(self):
        """
        Start listening for events on the task-events topic
        """
        await self.consume_events()

    def stop(self):
        """
        Stop the consumer
        """
        self.is_running = False
        self.logger.info("Task Event Consumer stopped")

    async def health_check(self) -> bool:
        """
        Perform a health check on the task event consumer

        Returns:
            True if the consumer is healthy, False otherwise
        """
        try:
            if not self.consumer:
                return False

            # Check if the consumer is still active
            # This is a simplified check; in a real system you'd check more metrics
            return True
        except Exception as e:
            self.logger.error(f"Task Event Consumer health check failed: {str(e)}")
            return False


# Global task event consumer instance
_task_event_consumer: Optional[TaskEventConsumer] = None


async def get_task_event_consumer(bootstrap_servers: str = "localhost:9092") -> TaskEventConsumer:
    """
    Get the singleton instance of the Task Event Consumer
    """
    global _task_event_consumer

    if _task_event_consumer is None:
        _task_event_consumer = TaskEventConsumer(bootstrap_servers=bootstrap_servers)

    return _task_event_consumer


# Function to start the task event consumer service
async def run_task_event_consumer(bootstrap_servers: str = "localhost:9092", group_id: str = "task-events-consumer-group"):
    """
    Run the task event consumer as a service
    """
    consumer = TaskEventConsumer(bootstrap_servers=bootstrap_servers, group_id=group_id)

    try:
        await consumer.start_listening()
    except KeyboardInterrupt:
        consumer.logger.info("Interrupt received, shutting down...")
        consumer.stop()
    except Exception as e:
        consumer.logger.error(f"Unexpected error in task event consumer: {str(e)}")
        consumer.stop()
    finally:
        await consumer.disconnect()


# Context manager for using the task event consumer
class TaskEventConsumerContext:
    """
    Context manager for using the task event consumer
    """
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "task-events-consumer-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id

    async def __aenter__(self):
        self.consumer = TaskEventConsumer(bootstrap_servers=self.bootstrap_servers, group_id=self.group_id)
        await self.consumer.connect()
        return self.consumer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.consumer.disconnect()