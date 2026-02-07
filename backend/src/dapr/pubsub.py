"""
Dapr Pub/Sub integration for the todo chatbot system.
Handles publishing and subscribing to events using Dapr's pub/sub building blocks.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime


class DaprPubSubService:
    """
    Service for interacting with Dapr Pub/Sub building blocks
    """

    def __init__(self, dapr_client=None, pubsub_name: str = "pubsub"):
        self.dapr_client = dapr_client
        self.pubsub_name = pubsub_name
        self.logger = logging.getLogger(__name__)
        self._subscriptions = {}

    async def connect(self):
        """
        Initialize and connect the Dapr client.
        """
        if not self.dapr_client:
            try:
                from dapr.clients import DaprClient
                self.dapr_client = DaprClient()
                self.logger.info("Initialized Dapr client for pub/sub")
            except ImportError:
                self.logger.error("Dapr client not available. Install dapr.")
                raise

    async def publish_event(self, topic: str, data: Dict[str, Any], metadata: Optional[Dict[str, str]] = None) -> bool:
        """
        Publish an event to a Dapr pub/sub topic.

        Args:
            topic: The topic to publish to
            data: The data to publish
            metadata: Optional metadata to include with the event

        Returns:
            True if the event was published successfully, False otherwise
        """
        await self.connect()

        try:
            # Create event payload
            event_payload = {
                "id": f"event-{int(datetime.utcnow().timestamp())}-{hash(str(data))}",
                "source": "todo-chatbot-backend",
                "type": f"com.todo.event.{topic.replace('-', '.')}",
                "specversion": "1.0",
                "datacontenttype": "application/json",
                "time": datetime.utcnow().isoformat(),
                "data": data
            }

            # Serialize the payload
            serialized_data = json.dumps(event_payload)

            # Publish to Dapr pub/sub
            if self.dapr_client:
                await self.dapr_client.publish_event(
                    pubsub_name=self.pubsub_name,
                    topic_name=topic,
                    data=serialized_data,
                    metadata=metadata or {}
                )

            self.logger.info(f"Published event to topic {topic}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish event to topic {topic}: {str(e)}")
            return False

    async def subscribe_to_topic(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to a Dapr pub/sub topic.

        Args:
            topic: The topic to subscribe to
            handler: The function to call when an event is received
        """
        # Note: In a real implementation, Dapr handles subscriptions differently
        # Usually you'd have a separate subscriber service that Dapr calls
        # This is a simplified implementation for demonstration

        self._subscriptions[topic] = handler
        self.logger.info(f"Subscribed to topic {topic}")

    async def handle_subscription(self, topic: str, message_data: str):
        """
        Handle a message received from a subscription.

        Args:
            topic: The topic the message came from
            message_data: The raw message data as a string
        """
        if topic not in self._subscriptions:
            self.logger.warning(f"No handler registered for topic {topic}")
            return

        try:
            # Parse the message data
            message_dict = json.loads(message_data)

            # Call the handler
            handler = self._subscriptions[topic]
            if asyncio.iscoroutinefunction(handler):
                await handler(message_dict)
            else:
                handler(message_dict)

            self.logger.info(f"Processed message from topic {topic}")
        except Exception as e:
            self.logger.error(f"Error handling message from topic {topic}: {str(e)}")

    async def publish_task_event(self, event_type: str, task_data: Dict[str, Any]) -> bool:
        """
        Publish a task-related event to the appropriate topic.

        Args:
            event_type: The type of task event (e.g., 'created', 'updated', 'deleted')
            task_data: The task data to include in the event

        Returns:
            True if the event was published successfully, False otherwise
        """
        topic = "task-events"
        event_data = {
            "event_type": event_type,
            "task": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self.publish_event(topic, event_data)

    async def publish_reminder_event(self, event_type: str, reminder_data: Dict[str, Any]) -> bool:
        """
        Publish a reminder-related event to the appropriate topic.

        Args:
            event_type: The type of reminder event (e.g., 'scheduled', 'triggered', 'cancelled')
            reminder_data: The reminder data to include in the event

        Returns:
            True if the event was published successfully, False otherwise
        """
        topic = "reminders"
        event_data = {
            "event_type": event_type,
            "reminder": reminder_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self.publish_event(topic, event_data)

    async def publish_task_update_event(self, event_type: str, update_data: Dict[str, Any]) -> bool:
        """
        Publish a task update event to the appropriate topic.

        Args:
            event_type: The type of update event (e.g., 'status-change', 'assignment')
            update_data: The update data to include in the event

        Returns:
            True if the event was published successfully, False otherwise
        """
        topic = "task-updates"
        event_data = {
            "event_type": event_type,
            "update": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self.publish_event(topic, event_data)

    async def health_check(self) -> bool:
        """
        Check if the Dapr pub/sub service is accessible.

        Returns:
            True if the service is accessible, False otherwise
        """
        try:
            # Try to initialize the Dapr client
            await self.connect()
            return True
        except Exception as e:
            self.logger.error(f"Dapr pub/sub health check failed: {str(e)}")
            return False


# Global instance of the Dapr PubSub Service
_dapr_pubsub_service: Optional[DaprPubSubService] = None


async def get_dapr_pubsub_service(dapr_client=None) -> DaprPubSubService:
    """
    Get the singleton instance of the Dapr PubSub Service.
    """
    global _dapr_pubsub_service

    if _dapr_pubsub_service is None:
        _dapr_pubsub_service = DaprPubSubService(dapr_client=dapr_client)

    return _dapr_pubsub_service


# Helper functions for common publishing operations
async def publish_task_created_event(task_data: Dict[str, Any], dapr_client=None) -> bool:
    """
    Helper function to publish a task created event.

    Args:
        task_data: The task data to include in the event
        dapr_client: Optional Dapr client instance

    Returns:
        True if the event was published successfully, False otherwise
    """
    pubsub_service = await get_dapr_pubsub_service(dapr_client)
    return await pubsub_service.publish_task_event("created", task_data)


async def publish_task_updated_event(task_data: Dict[str, Any], dapr_client=None) -> bool:
    """
    Helper function to publish a task updated event.

    Args:
        task_data: The task data to include in the event
        dapr_client: Optional Dapr client instance

    Returns:
        True if the event was published successfully, False otherwise
    """
    pubsub_service = await get_dapr_pubsub_service(dapr_client)
    return await pubsub_service.publish_task_event("updated", task_data)


async def publish_task_deleted_event(task_data: Dict[str, Any], dapr_client=None) -> bool:
    """
    Helper function to publish a task deleted event.

    Args:
        task_data: The task data to include in the event
        dapr_client: Optional Dapr client instance

    Returns:
        True if the event was published successfully, False otherwise
    """
    pubsub_service = await get_dapr_pubsub_service(dapr_client)
    return await pubsub_service.publish_task_event("deleted", task_data)


async def publish_reminder_scheduled_event(reminder_data: Dict[str, Any], dapr_client=None) -> bool:
    """
    Helper function to publish a reminder scheduled event.

    Args:
        reminder_data: The reminder data to include in the event
        dapr_client: Optional Dapr client instance

    Returns:
        True if the event was published successfully, False otherwise
    """
    pubsub_service = await get_dapr_pubsub_service(dapr_client)
    return await pubsub_service.publish_reminder_event("scheduled", reminder_data)


async def publish_reminder_triggered_event(reminder_data: Dict[str, Any], dapr_client=None) -> bool:
    """
    Helper function to publish a reminder triggered event.

    Args:
        reminder_data: The reminder data to include in the event
        dapr_client: Optional Dapr client instance

    Returns:
        True if the event was published successfully, False otherwise
    """
    pubsub_service = await get_dapr_pubsub_service(dapr_client)
    return await pubsub_service.publish_reminder_event("triggered", reminder_data)


# Context manager for using the Dapr PubSub service
class DaprPubSubServiceContext:
    """
    Context manager for using the Dapr PubSub service.
    Ensures proper initialization and cleanup.
    """
    def __init__(self, dapr_client=None, pubsub_name: str = "pubsub"):
        self.dapr_client = dapr_client
        self.pubsub_name = pubsub_name

    async def __aenter__(self):
        self.service = DaprPubSubService(dapr_client=self.dapr_client, pubsub_name=self.pubsub_name)
        await self.service.connect()
        return self.service

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup operations if needed
        pass