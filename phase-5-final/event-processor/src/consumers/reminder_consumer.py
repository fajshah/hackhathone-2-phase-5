"""
Reminder Events Kafka Consumer for the todo chatbot system.
Consumes reminder-related events from the reminders topic.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from ..processors.event_processor import EventProcessor


class ReminderEventConsumer:
    """
    Consumer for the reminders Kafka topic
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092",
                 group_id: str = "reminder-events-consumer-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Event processor to handle events
        self.event_processor = None

    async def connect(self):
        """
        Initialize and connect the Kafka consumer for reminders topic
        """
        self.consumer = AIOKafkaConsumer(
            'reminders',  # Subscribe to reminders topic
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',  # Start from the beginning of the topic
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
        )

        await self.consumer.start()
        self.logger.info(f"Reminder Event Consumer connected to Kafka at {self.bootstrap_servers}")

    async def disconnect(self):
        """
        Disconnect and close the Kafka consumer
        """
        if self.consumer:
            await self.consumer.stop()
            self.logger.info("Reminder Event Consumer disconnected from Kafka")

    async def process_reminder_event(self, event_data: Dict[str, Any]):
        """
        Process a reminder-related event from the reminders topic

        Args:
            event_data: The event data to process
        """
        try:
            event_type = event_data.get('event_type', 'unknown')

            self.logger.info(f"Processing reminder event: {event_type}, ID: {event_data.get('id', 'unknown')}")

            # Handle different reminder event types
            if event_type == 'reminder.scheduled':
                await self._handle_reminder_scheduled(event_data)
            elif event_type == 'reminder.triggered':
                await self._handle_reminder_triggered(event_data)
            elif event_type == 'reminder.cancelled':
                await self._handle_reminder_cancelled(event_data)
            elif event_type == 'reminder.sent':
                await self._handle_reminder_sent(event_data)
            else:
                self.logger.warning(f"Unknown reminder event type: {event_type}")

        except Exception as e:
            self.logger.error(f"Error processing reminder event {event_data.get('event_type', 'unknown')}: {str(e)}")
            # In a real implementation, you might send this to a dead-letter queue
            raise

    async def _handle_reminder_scheduled(self, event_data: Dict[str, Any]):
        """
        Handle a reminder scheduled event

        Args:
            event_data: The reminder scheduled event data
        """
        reminder_data = event_data.get('payload', {}).get('reminder', {})

        self.logger.info(f"Handling reminder scheduled event for reminder: {reminder_data.get('id')}")

        # In a real implementation:
        # - Schedule the actual notification at the specified time
        # - Store the reminder in a persistent store for tracking
        # - Prepare for delivery at the scheduled time

        # Example: Log the event
        print(f"Reminder scheduled: For task {reminder_data.get('task_id', 'Unknown task')} "
              f"at {reminder_data.get('scheduled_time', 'Unknown time')} (ID: {reminder_data.get('id')})")

    async def _handle_reminder_triggered(self, event_data: Dict[str, Any]):
        """
        Handle a reminder triggered event

        Args:
            event_data: The reminder triggered event data
        """
        reminder_data = event_data.get('payload', {}).get('reminder', {})

        self.logger.info(f"Handling reminder triggered event for reminder: {reminder_data.get('id')}")

        # In a real implementation:
        # - Send the actual notification to the user
        # - Update the reminder status to triggered
        # - Track the delivery status

        # Example: Log the event
        print(f"Reminder triggered: For task {reminder_data.get('task_id', 'Unknown task')} "
              f"at {datetime.utcnow().isoformat()} (ID: {reminder_data.get('id')})")

    async def _handle_reminder_cancelled(self, event_data: Dict[str, Any]):
        """
        Handle a reminder cancelled event

        Args:
            event_data: The reminder cancelled event data
        """
        reminder_data = event_data.get('payload', {}).get('reminder', {})

        self.logger.info(f"Handling reminder cancelled event for reminder: {reminder_data.get('id')}")

        # In a real implementation:
        # - Cancel any scheduled notifications
        # - Update the reminder status to cancelled
        # - Clean up any related resources

        # Example: Log the event
        print(f"Reminder cancelled: For task {reminder_data.get('task_id', 'Unknown task')} "
              f"(ID: {reminder_data.get('id')})")

    async def _handle_reminder_sent(self, event_data: Dict[str, Any]):
        """
        Handle a reminder sent event

        Args:
            event_data: The reminder sent event data
        """
        reminder_data = event_data.get('payload', {}).get('reminder', {})

        self.logger.info(f"Handling reminder sent event for reminder: {reminder_data.get('id')}")

        # In a real implementation:
        # - Update the reminder status to sent
        # - Record the delivery time
        # - Track delivery metrics

        # Example: Log the event
        print(f"Reminder sent: For task {reminder_data.get('task_id', 'Unknown task')} "
              f"at {datetime.utcnow().isoformat()} (ID: {reminder_data.get('id')})")

    async def consume_events(self):
        """
        Main consumption loop for reminders topic
        """
        if not self.consumer:
            await self.connect()

        self.is_running = True
        self.logger.info("Starting reminder event consumption loop...")

        try:
            while self.is_running:
                # Consume messages from the reminders topic
                msg = await self.consumer.getone()

                if msg:
                    try:
                        # Process the reminder event
                        event_data = msg.value
                        await self.process_reminder_event(event_data)

                        # Commit the offset after processing
                        await self.consumer.commit()

                    except Exception as e:
                        self.logger.error(f"Error processing reminder event from {msg.topic}:{msg.partition}@{msg.offset}: {str(e)}")
                        # Don't commit the offset on error so the message can be retried
                        continue
                else:
                    # Small delay to prevent busy-waiting
                    await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Error in reminder event consumption loop: {str(e)}")
        finally:
            await self.disconnect()

    async def start_listening(self):
        """
        Start listening for events on the reminders topic
        """
        await self.consume_events()

    def stop(self):
        """
        Stop the consumer
        """
        self.is_running = False
        self.logger.info("Reminder Event Consumer stopped")

    async def health_check(self) -> bool:
        """
        Perform a health check on the reminder event consumer

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
            self.logger.error(f"Reminder Event Consumer health check failed: {str(e)}")
            return False


# Global reminder event consumer instance
_reminder_event_consumer: Optional[ReminderEventConsumer] = None


async def get_reminder_event_consumer(bootstrap_servers: str = "localhost:9092") -> ReminderEventConsumer:
    """
    Get the singleton instance of the Reminder Event Consumer
    """
    global _reminder_event_consumer

    if _reminder_event_consumer is None:
        _reminder_event_consumer = ReminderEventConsumer(bootstrap_servers=bootstrap_servers)

    return _reminder_event_consumer


# Function to start the reminder event consumer service
async def run_reminder_event_consumer(bootstrap_servers: str = "localhost:9092", group_id: str = "reminder-events-consumer-group"):
    """
    Run the reminder event consumer as a service
    """
    consumer = ReminderEventConsumer(bootstrap_servers=bootstrap_servers, group_id=group_id)

    try:
        await consumer.start_listening()
    except KeyboardInterrupt:
        consumer.logger.info("Interrupt received, shutting down...")
        consumer.stop()
    except Exception as e:
        consumer.logger.error(f"Unexpected error in reminder event consumer: {str(e)}")
        consumer.stop()
    finally:
        await consumer.disconnect()


# Context manager for using the reminder event consumer
class ReminderEventConsumerContext:
    """
    Context manager for using the reminder event consumer
    """
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "reminder-events-consumer-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id

    async def __aenter__(self):
        self.consumer = ReminderEventConsumer(bootstrap_servers=self.bootstrap_servers, group_id=self.group_id)
        await self.consumer.connect()
        return self.consumer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.consumer.disconnect()