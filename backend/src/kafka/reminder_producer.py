"""
Kafka producer for reminder events in the todo chatbot system.
Handles publishing reminder-related events to Kafka topics.
"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import aiokafka
from aiokafka import AIOKafkaProducer
import logging


class ReminderEventType(str, Enum):
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_CANCELLED = "reminder.cancelled"
    REMINDER_TRIGGERED = "reminder.triggered"
    REMINDER_SENT = "reminder.sent"


class ReminderEventProducer:
    """
    Kafka producer for publishing reminder-related events
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

    async def publish_reminder_event(self, event_type: ReminderEventType, reminder_data: Dict[str, Any],
                                  correlation_id: Optional[str] = None):
        """
        Publish a reminder event to the appropriate Kafka topic.

        Args:
            event_type: The type of reminder event
            reminder_data: The reminder data to include in the event
            correlation_id: Optional correlation ID for tracking related events
        """
        await self.ensure_connection()

        # Create the event payload
        event_payload = {
            "event_type": event_type.value,
            "event_id": f"reminder-event-{int(datetime.utcnow().timestamp())}-{hash(str(reminder_data))}",
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id or f"corr-{int(datetime.utcnow().timestamp())}",
            "source_service": "todo-chatbot-backend",
            "payload": {
                "reminder": reminder_data
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

    async def publish_reminder_scheduled(self, reminder_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a reminder scheduled event.
        """
        return await self.publish_reminder_event(
            event_type=ReminderEventType.REMINDER_SCHEDULED,
            reminder_data=reminder_data,
            correlation_id=correlation_id
        )

    async def publish_reminder_cancelled(self, reminder_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a reminder cancelled event.
        """
        return await self.publish_reminder_event(
            event_type=ReminderEventType.REMINDER_CANCELLED,
            reminder_data=reminder_data,
            correlation_id=correlation_id
        )

    async def publish_reminder_triggered(self, reminder_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a reminder triggered event.
        """
        return await self.publish_reminder_event(
            event_type=ReminderEventType.REMINDER_TRIGGERED,
            reminder_data=reminder_data,
            correlation_id=correlation_id
        )

    async def publish_reminder_sent(self, reminder_data: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Publish a reminder sent event.
        """
        return await self.publish_reminder_event(
            event_type=ReminderEventType.REMINDER_SENT,
            reminder_data=reminder_data,
            correlation_id=correlation_id
        )

    def _get_topic_name(self, event_type: ReminderEventType) -> str:
        """
        Get the appropriate Kafka topic name based on the event type.

        For this system, we use:
        - reminders: For all reminder events
        """
        if event_type in [ReminderEventType.REMINDER_SCHEDULED, ReminderEventType.REMINDER_CANCELLED,
                         ReminderEventType.REMINDER_TRIGGERED, ReminderEventType.REMINDER_SENT]:
            return f"{self.topic_prefix}reminders" if self.topic_prefix else "reminders"
        else:
            return f"{self.topic_prefix}reminders" if self.topic_prefix else "reminders"

    async def health_check(self) -> bool:
        """
        Check if the Kafka producer is healthy and connected.
        """
        try:
            if not self.is_connected or not self.producer:
                return False

            # Try to send a simple test message to a test topic
            test_payload = {
                "event_type": "health.check",
                "timestamp": datetime.utcnow().isoformat(),
                "source_service": "todo-chatbot-backend",
                "payload": {"status": "ok"}
            }

            # Send to a test topic (we'll use reminders for this check)
            future = await self.producer.send_and_wait(
                f"{self.topic_prefix}reminders" if self.topic_prefix else "reminders",
                test_payload
            )

            self.logger.debug("Kafka reminder producer health check passed")
            return True

        except Exception as e:
            self.logger.error(f"Kafka reminder producer health check failed: {str(e)}")
            return False


# Singleton producer instance
_reminder_kafka_producer_instance: Optional[ReminderEventProducer] = None


async def get_reminder_event_producer() -> ReminderEventProducer:
    """
    Get the singleton instance of the reminder event producer.
    """
    global _reminder_kafka_producer_instance

    if _reminder_kafka_producer_instance is None:
        # Get configuration from environment or use defaults
        import os
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        topic_prefix = os.getenv("KAFKA_TOPIC_PREFIX", "")

        _reminder_kafka_producer_instance = ReminderEventProducer(
            bootstrap_servers=bootstrap_servers,
            topic_prefix=topic_prefix
        )

    return _reminder_kafka_producer_instance


# Context manager for using the producer
class ReminderEventProducerContext:
    """
    Context manager for using the reminder event producer.
    Ensures proper connection and disconnection.
    """
    def __init__(self, producer: ReminderEventProducer):
        self.producer = producer

    async def __aenter__(self):
        await self.producer.connect()
        return self.producer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.producer.disconnect()