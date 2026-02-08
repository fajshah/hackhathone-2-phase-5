"""
Kafka producer for task events in the todo chatbot system.
Handles publishing task-related events to Kafka topics.
"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import aiokafka
from aiokafka import AIOKafkaProducer
import logging


class TaskEventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_COMPLETED = "task.completed"
    TASK_ASSIGNED = "task.assigned"


class TaskEventProducer:
    """
    Kafka producer for publishing task-related events
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092", topic_prefix: str = ""):
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix
        self.producer: Optional[AIOKafkaProducer] = None
        self.is_connected = False
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        """
        Initialize and connect the Kafka producer.
        """
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                compression_type='gzip',
                linger_ms=5,  # Small delay to batch messages
            )

            # Start the producer
            await self.producer.start()
            self.is_connected = True
            self.logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Kafka: {str(e)}")
            raise

    async def disconnect(self):
        """
        Disconnect and close the Kafka producer.
        """
        if self.producer:
            await self.producer.stop()
            self.is_connected = False
            self.logger.info("Disconnected from Kafka")

    async def ensure_connection(self):
        """
        Ensure the producer is connected, connecting if necessary.
        """
        if not self.is_connected:
            await self.connect()

    async def publish_task_event(self, event_type: TaskEventType, task_data: Dict[str, Any],
                               correlation_id: Optional[str] = None):
        """
        Publish a task event to the appropriate Kafka topic.

        Args:
            event_type: The type of task event
            task_data: The task data to include in the event
            correlation_id: Optional correlation ID for tracking related events
        """
        await self.ensure_connection()

        # Create the event payload
        event_payload = {
            "event_type": event_type.value,
            "event_id": f"task-event-{int(datetime.utcnow().timestamp())}-{hash(str(task_data))}",
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id or f"corr-{int(datetime.utcnow().timestamp())}",
            "source_service": "todo-chatbot-backend",
            "payload": {
                "task": task_data
            }
        }

        # Determine the topic based on the event type
        topic = self._get_topic_name(event_type)

        try:
            # Send the message
            future = await self.producer.send_and_wait(
                topic,
                event_payload
            )

            self.logger.info(f"Published {event_type.value} event to topic {topic}, "
                           f"partition {future.partition}, offset {future.offset}")

            return future

        except Exception as e:
            self.logger.error(f"Failed to publish {event_type.value} event: {str(e)}")
            raise

    async def publish_task_created(self, task_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a task created event.
        """
        return await self.publish_task_event(
            event_type=TaskEventType.TASK_CREATED,
            task_data=task_data,
            correlation_id=correlation_id
        )

    async def publish_task_updated(self, task_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a task updated event.
        """
        return await self.publish_task_event(
            event_type=TaskEventType.TASK_UPDATED,
            task_data=task_data,
            correlation_id=correlation_id
        )

    async def publish_task_deleted(self, task_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a task deleted event.
        """
        return await self.publish_task_event(
            event_type=TaskEventType.TASK_DELETED,
            task_data=task_data,
            correlation_id=correlation_id
        )

    async def publish_task_completed(self, task_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a task completed event.
        """
        return await self.publish_task_event(
            event_type=TaskEventType.TASK_COMPLETED,
            task_data=task_data,
            correlation_id=correlation_id
        )

    async def publish_task_assigned(self, task_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a task assigned event.
        """
        return await self.publish_task_event(
            event_type=TaskEventType.TASK_ASSIGNED,
            task_data=task_data,
            correlation_id=correlation_id
        )

    def _get_topic_name(self, event_type: TaskEventType) -> str:
        """
        Get the appropriate Kafka topic name based on the event type.

        For this system, we use:
        - task-events: For task lifecycle events
        - task-updates: For task status changes
        """
        if event_type in [TaskEventType.TASK_CREATED, TaskEventType.TASK_UPDATED,
                         TaskEventType.TASK_DELETED, TaskEventType.TASK_COMPLETED]:
            return f"{self.topic_prefix}task-events" if self.topic_prefix else "task-events"
        elif event_type in [TaskEventType.TASK_ASSIGNED]:
            return f"{self.topic_prefix}task-updates" if self.topic_prefix else "task-updates"
        else:
            return f"{self.topic_prefix}task-events" if self.topic_prefix else "task-events"

    async def health_check(self) -> bool:
        """
        Check if the Kafka producer is healthy and connected.
        """
        try:
            if not self.is_connected or not self.producer:
                return False

            # Try to send a simple test message to a test topic
            # This is a basic check to see if the producer is functional
            test_payload = {
                "event_type": "health.check",
                "timestamp": datetime.utcnow().isoformat(),
                "source_service": "todo-chatbot-backend",
                "payload": {"status": "ok"}
            }

            # Send to a test topic (we'll use task-events for this check)
            future = await self.producer.send_and_wait(
                f"{self.topic_prefix}task-events" if self.topic_prefix else "task-events",
                test_payload
            )

            self.logger.debug("Kafka health check passed")
            return True

        except Exception as e:
            self.logger.error(f"Kafka health check failed: {str(e)}")
            return False


# Singleton producer instance
_kafka_producer_instance: Optional[TaskEventProducer] = None


async def get_task_event_producer() -> TaskEventProducer:
    """
    Get the singleton instance of the task event producer.
    """
    global _kafka_producer_instance

    if _kafka_producer_instance is None:
        # Get configuration from environment or use defaults
        import os
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        topic_prefix = os.getenv("KAFKA_TOPIC_PREFIX", "")

        _kafka_producer_instance = TaskEventProducer(
            bootstrap_servers=bootstrap_servers,
            topic_prefix=topic_prefix
        )

    return _kafka_producer_instance


# Context manager for using the producer
class TaskEventProducerContext:
    """
    Context manager for using the task event producer.
    Ensures proper connection and disconnection.
    """
    def __init__(self, producer: TaskEventProducer):
        self.producer = producer

    async def __aenter__(self):
        await self.producer.connect()
        return self.producer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.producer.disconnect()