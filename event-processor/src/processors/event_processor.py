"""
Event Processor service for the todo chatbot system.
Consumes and processes events from Kafka topics.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from aiokafka import AIOKafkaConsumer
import signal
import sys


class EventProcessor:
    """
    Main event processor that consumes events from Kafka and processes them
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "event-processor-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Event handlers dictionary
        self.event_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """
        Set up signal handlers for graceful shutdown
        """
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def connect(self):
        """
        Initialize and connect the Kafka consumer
        """
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',  # Start from the beginning of the topic
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
        )

        await self.consumer.start()
        self.logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        self.is_running = True

    async def disconnect(self):
        """
        Disconnect and close the Kafka consumer
        """
        if self.consumer:
            await self.consumer.stop()
            self.is_running = False
            self.logger.info("Disconnected from Kafka")

    async def register_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Register a handler for a specific event type

        Args:
            event_type: The type of event to handle
            handler: The function to call when this event type is received
        """
        self.event_handlers[event_type] = handler
        self.logger.info(f"Registered handler for event type: {event_type}")

    async def process_event(self, event_data: Dict[str, Any]):
        """
        Process an incoming event based on its type

        Args:
            event_data: The event data to process
        """
        try:
            event_type = event_data.get('event_type', 'unknown')

            self.logger.info(f"Processing event: {event_type}, ID: {event_data.get('id', 'unknown')}")

            # Check if there's a specific handler for this event type
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]

                # Process the event with the registered handler
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)

                self.logger.info(f"Event {event_type} processed successfully")
            else:
                # If no specific handler, log a warning
                self.logger.warning(f"No handler registered for event type: {event_type}")

                # Process with default handler
                await self._default_event_handler(event_data)

        except Exception as e:
            self.logger.error(f"Error processing event {event_data.get('event_type', 'unknown')}: {str(e)}")
            # In a real implementation, you might send this to a dead-letter queue
            raise

    async def _default_event_handler(self, event_data: Dict[str, Any]):
        """
        Default handler for events without specific handlers

        Args:
            event_data: The event data to process
        """
        self.logger.info(f"Default handler processing event: {event_data.get('event_type', 'unknown')}")
        # In a real implementation, you might log this to a generic audit log
        pass

    async def consume_events(self, topics: list):
        """
        Consume events from the specified topics

        Args:
            topics: List of topics to consume from
        """
        if not self.consumer:
            await self.connect()

        # Subscribe to the topics
        self.consumer.subscribe(topics=topics)
        self.logger.info(f"Subscribed to topics: {topics}")

        try:
            while self.is_running:
                # Consume messages
                msg = await self.consumer.getone()

                if msg:
                    try:
                        # Process the event
                        event_data = msg.value
                        await self.process_event(event_data)

                        # Commit the offset after processing
                        await self.consumer.commit()

                    except Exception as e:
                        self.logger.error(f"Error processing message from {msg.topic}:{msg.partition}@{msg.offset}: {str(e)}")
                        # Don't commit the offset on error so the message can be retried
                        continue
                else:
                    # Small delay to prevent busy-waiting
                    await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Error in event consumption loop: {str(e)}")
        finally:
            await self.disconnect()

    async def start_processing(self, topics: list):
        """
        Start the event processing loop

        Args:
            topics: List of topics to consume from
        """
        self.logger.info("Starting event processor...")
        await self.consume_events(topics)

    def stop(self):
        """
        Stop the event processor
        """
        self.is_running = False
        self.logger.info("Event processor stopped")

    async def health_check(self) -> bool:
        """
        Perform a health check on the event processor

        Returns:
            True if the processor is healthy, False otherwise
        """
        try:
            # Check if consumer is connected and subscribed to topics
            if not self.consumer:
                return False

            # Check if the consumer is still active
            # This is a simplified check; in a real system you'd check more metrics
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    async def get_consumer_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the consumer

        Returns:
            Dictionary with consumer metrics
        """
        try:
            if not self.consumer:
                return {"error": "Consumer not initialized"}

            # In a real implementation, you would get detailed consumer metrics
            # This is a simplified version
            metrics = {
                "connected": True,
                "topics_subscribed": list(self.consumer.topics()),
                "group_id": self.group_id,
                "bootstrap_servers": self.bootstrap_servers,
                "timestamp": datetime.utcnow().isoformat()
            }

            return metrics
        except Exception as e:
            self.logger.error(f"Error getting consumer metrics: {str(e)}")
            return {"error": str(e)}


class TaskEventHandler:
    """
    Handler for task-related events
    """

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    async def handle_task_created(self, event_data: Dict[str, Any]):
        """
        Handle a task created event
        """
        task_data = event_data.get('payload', {}).get('task', {})
        self.logger.info(f"Handling task created event for task: {task_data.get('id')}")

        # In a real implementation, you would update the database or trigger other actions
        # For now, just log the event
        pass

    async def handle_task_updated(self, event_data: Dict[str, Any]):
        """
        Handle a task updated event
        """
        task_data = event_data.get('payload', {}).get('task', {})
        self.logger.info(f"Handling task updated event for task: {task_data.get('id')}")

        # In a real implementation, you would update the database or trigger other actions
        # For now, just log the event
        pass

    async def handle_task_deleted(self, event_data: Dict[str, Any]):
        """
        Handle a task deleted event
        """
        task_data = event_data.get('payload', {}).get('task', {})
        self.logger.info(f"Handling task deleted event for task: {task_data.get('id')}")

        # In a real implementation, you would update the database or trigger other actions
        # For now, just log the event
        pass


class ReminderEventHandler:
    """
    Handler for reminder-related events
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def handle_reminder_scheduled(self, event_data: Dict[str, Any]):
        """
        Handle a reminder scheduled event
        """
        reminder_data = event_data.get('payload', {}).get('reminder', {})
        self.logger.info(f"Handling reminder scheduled event for reminder: {reminder_data.get('id')}")

        # In a real implementation, you would trigger notification scheduling
        # For now, just log the event
        pass

    async def handle_reminder_triggered(self, event_data: Dict[str, Any]):
        """
        Handle a reminder triggered event
        """
        reminder_data = event_data.get('payload', {}).get('reminder', {})
        self.logger.info(f"Handling reminder triggered event for reminder: {reminder_data.get('id')}")

        # In a real implementation, you would trigger notification sending
        # For now, just log the event
        pass

    async def handle_reminder_cancelled(self, event_data: Dict[str, Any]):
        """
        Handle a reminder cancelled event
        """
        reminder_data = event_data.get('payload', {}).get('reminder', {})
        self.logger.info(f"Handling reminder cancelled event for reminder: {reminder_data.get('id')}")

        # In a real implementation, you would cancel the notification
        # For now, just log the event
        pass


# Global event processor instance
_event_processor: Optional[EventProcessor] = None


async def get_event_processor(bootstrap_servers: str = "localhost:9092") -> EventProcessor:
    """
    Get the singleton instance of the Event Processor
    """
    global _event_processor

    if _event_processor is None:
        _event_processor = EventProcessor(bootstrap_servers=bootstrap_servers)

    return _event_processor


async def setup_default_event_handlers(event_processor: EventProcessor):
    """
    Set up default event handlers for common event types
    """
    # Create handler instances
    task_handler = TaskEventHandler()
    reminder_handler = ReminderEventHandler()

    # Register handlers for task events
    await event_processor.register_event_handler('task.created', task_handler.handle_task_created)
    await event_processor.register_event_handler('task.updated', task_handler.handle_task_updated)
    await event_processor.register_event_handler('task.deleted', task_handler.handle_task_deleted)

    # Register handlers for reminder events
    await event_processor.register_event_handler('reminder.scheduled', reminder_handler.handle_reminder_scheduled)
    await event_processor.register_event_handler('reminder.triggered', reminder_handler.handle_reminder_triggered)
    await event_processor.register_event_handler('reminder.cancelled', reminder_handler.handle_reminder_cancelled)


# Context manager for using the event processor
class EventProcessorContext:
    """
    Context manager for using the event processor
    """
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "event-processor-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id

    async def __aenter__(self):
        self.processor = EventProcessor(bootstrap_servers=self.bootstrap_servers, group_id=self.group_id)
        await self.processor.connect()
        await setup_default_event_handlers(self.processor)
        return self.processor

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.processor.disconnect()