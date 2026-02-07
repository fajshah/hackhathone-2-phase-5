"""
Task Update Events Kafka Consumer for the todo chatbot system.
Consumes task update-related events from the task-updates topic.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from ..processors.event_processor import EventProcessor


class UpdateEventConsumer:
    """
    Consumer for the task-updates Kafka topic
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092",
                 group_id: str = "update-events-consumer-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)

        # Event processor to handle events
        self.event_processor = None

    async def connect(self):
        """
        Initialize and connect the Kafka consumer for task-updates
        """
        self.consumer = AIOKafkaConsumer(
            'task-updates',  # Subscribe to task-updates topic
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',  # Start from the beginning of the topic
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
        )

        await self.consumer.start()
        self.logger.info(f"Update Event Consumer connected to Kafka at {self.bootstrap_servers}")

    async def disconnect(self):
        """
        Disconnect and close the Kafka consumer
        """
        if self.consumer:
            await self.consumer.stop()
            self.logger.info("Update Event Consumer disconnected from Kafka")

    async def process_update_event(self, event_data: Dict[str, Any]):
        """
        Process a task update-related event from the task-updates topic

        Args:
            event_data: The event data to process
        """
        try:
            event_type = event_data.get('event_type', 'unknown')

            self.logger.info(f"Processing update event: {event_type}, ID: {event_data.get('id', 'unknown')}")

            # Handle different update event types
            if event_type == 'task.status-changed':
                await self._handle_task_status_changed(event_data)
            elif event_type == 'task.assigned':
                await self._handle_task_assigned(event_data)
            elif event_type == 'task.reassigned':
                await self._handle_task_reassigned(event_data)
            elif event_type == 'task.priority-changed':
                await self._handle_task_priority_changed(event_data)
            elif event_type == 'task.due-date-changed':
                await self._handle_task_due_date_changed(event_data)
            elif event_type == 'task.title-updated':
                await self._handle_task_title_updated(event_data)
            elif event_type == 'task.description-updated':
                await self._handle_task_description_updated(event_data)
            elif event_type == 'task.tag-added':
                await self._handle_task_tag_added(event_data)
            elif event_type == 'task.tag-removed':
                await self._handle_task_tag_removed(event_data)
            elif event_type == 'task.comment-added':
                await self._handle_task_comment_added(event_data)
            else:
                self.logger.warning(f"Unknown update event type: {event_type}")
                # Handle any other update event generically
                await self._handle_generic_update(event_data)

        except Exception as e:
            self.logger.error(f"Error processing update event {event_data.get('event_type', 'unknown')}: {str(e)}")
            # In a real implementation, you might send this to a dead-letter queue
            raise

    async def _handle_task_status_changed(self, event_data: Dict[str, Any]):
        """
        Handle a task status changed event

        Args:
            event_data: The task status changed event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        old_status = update_data.get('old_status', 'unknown')
        new_status = update_data.get('new_status', 'unknown')

        self.logger.info(f"Handling task status changed event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Trigger any related workflows based on status change
        # - Update metrics or analytics systems
        # - Possibly trigger notifications to interested parties

        # Example: Log the event
        print(f"Task status changed: {task_id} - {old_status} → {new_status}")

    async def _handle_task_assigned(self, event_data: Dict[str, Any]):
        """
        Handle a task assigned event

        Args:
            event_data: The task assigned event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        assigned_to = update_data.get('assigned_to', 'unassigned')

        self.logger.info(f"Handling task assigned event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Notify the assignee
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task assigned: {task_id} → {assigned_to}")

    async def _handle_task_reassigned(self, event_data: Dict[str, Any]):
        """
        Handle a task reassigned event

        Args:
            event_data: The task reassigned event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        old_assignee = update_data.get('old_assignee', 'unassigned')
        new_assignee = update_data.get('new_assignee', 'unassigned')

        self.logger.info(f"Handling task reassigned event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Notify both old and new assignees
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task reassigned: {task_id} - {old_assignee} → {new_assignee}")

    async def _handle_task_priority_changed(self, event_data: Dict[str, Any]):
        """
        Handle a task priority changed event

        Args:
            event_data: The task priority changed event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        old_priority = update_data.get('old_priority', 'unknown')
        new_priority = update_data.get('new_priority', 'unknown')

        self.logger.info(f"Handling task priority changed event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Possibly adjust processing priorities
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task priority changed: {task_id} - {old_priority} → {new_priority}")

    async def _handle_task_due_date_changed(self, event_data: Dict[str, Any]):
        """
        Handle a task due date changed event

        Args:
            event_data: The task due date changed event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        old_due_date = update_data.get('old_due_date', 'unknown')
        new_due_date = update_data.get('new_due_date', 'unknown')

        self.logger.info(f"Handling task due date changed event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Adjust any related scheduling
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task due date changed: {task_id} - {old_due_date} → {new_due_date}")

    async def _handle_task_title_updated(self, event_data: Dict[str, Any]):
        """
        Handle a task title updated event

        Args:
            event_data: The task title updated event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        old_title = update_data.get('old_title', 'unknown')
        new_title = update_data.get('new_title', 'unknown')

        self.logger.info(f"Handling task title updated event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Update any references to the task
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task title updated: {task_id} - '{old_title}' → '{new_title}'")

    async def _handle_task_description_updated(self, event_data: Dict[str, Any]):
        """
        Handle a task description updated event

        Args:
            event_data: The task description updated event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        old_description = update_data.get('old_description', 'unknown')
        new_description = update_data.get('new_description', 'unknown')

        self.logger.info(f"Handling task description updated event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Update any references to the task description
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Task description updated for: {task_id}")

    async def _handle_task_tag_added(self, event_data: Dict[str, Any]):
        """
        Handle a task tag added event

        Args:
            event_data: The task tag added event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        tag_added = update_data.get('tag', 'unknown')

        self.logger.info(f"Handling task tag added event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Update tag-related analytics
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Tag added to task: {task_id} - {tag_added}")

    async def _handle_task_tag_removed(self, event_data: Dict[str, Any]):
        """
        Handle a task tag removed event

        Args:
            event_data: The task tag removed event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        tag_removed = update_data.get('tag', 'unknown')

        self.logger.info(f"Handling task tag removed event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Update tag-related analytics
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Tag removed from task: {task_id} - {tag_removed}")

    async def _handle_task_comment_added(self, event_data: Dict[str, Any]):
        """
        Handle a task comment added event

        Args:
            event_data: The task comment added event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        task_id = update_data.get('task_id', 'unknown')
        comment_id = update_data.get('comment_id', 'unknown')

        self.logger.info(f"Handling task comment added event for task: {task_id}")

        # In a real implementation:
        # - Update any internal state or cache
        # - Notify interested parties
        # - Update metrics or analytics systems

        # Example: Log the event
        print(f"Comment added to task: {task_id} - Comment ID: {comment_id}")

    async def _handle_generic_update(self, event_data: Dict[str, Any]):
        """
        Handle any generic update event

        Args:
            event_data: The generic update event data
        """
        update_data = event_data.get('payload', {}).get('update', {})
        event_type = event_data.get('event_type', 'unknown')
        task_id = update_data.get('task_id', 'unknown')

        self.logger.info(f"Handling generic update event of type {event_type} for task: {task_id}")

        # Example: Log the event
        print(f"Generic update event: {event_type} for task {task_id}")

    async def consume_events(self):
        """
        Main consumption loop for task-updates topic
        """
        if not self.consumer:
            await self.connect()

        self.is_running = True
        self.logger.info("Starting update event consumption loop...")

        try:
            while self.is_running:
                # Consume messages from the task-updates topic
                msg = await self.consumer.getone()

                if msg:
                    try:
                        # Process the update event
                        event_data = msg.value
                        await self.process_update_event(event_data)

                        # Commit the offset after processing
                        await self.consumer.commit()

                    except Exception as e:
                        self.logger.error(f"Error processing update event from {msg.topic}:{msg.partition}@{msg.offset}: {str(e)}")
                        # Don't commit the offset on error so the message can be retried
                        continue
                else:
                    # Small delay to prevent busy-waiting
                    await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Error in update event consumption loop: {str(e)}")
        finally:
            await self.disconnect()

    async def start_listening(self):
        """
        Start listening for events on the task-updates topic
        """
        await self.consume_events()

    def stop(self):
        """
        Stop the consumer
        """
        self.is_running = False
        self.logger.info("Update Event Consumer stopped")

    async def health_check(self) -> bool:
        """
        Perform a health check on the update event consumer

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
            self.logger.error(f"Update Event Consumer health check failed: {str(e)}")
            return False


# Global update event consumer instance
_update_event_consumer: Optional[UpdateEventConsumer] = None


async def get_update_event_consumer(bootstrap_servers: str = "localhost:9092") -> UpdateEventConsumer:
    """
    Get the singleton instance of the Update Event Consumer
    """
    global _update_event_consumer

    if _update_event_consumer is None:
        _update_event_consumer = UpdateEventConsumer(bootstrap_servers=bootstrap_servers)

    return _update_event_consumer


# Function to start the update event consumer service
async def run_update_event_consumer(bootstrap_servers: str = "localhost:9092", group_id: str = "update-events-consumer-group"):
    """
    Run the update event consumer as a service
    """
    consumer = UpdateEventConsumer(bootstrap_servers=bootstrap_servers, group_id=group_id)

    try:
        await consumer.start_listening()
    except KeyboardInterrupt:
        consumer.logger.info("Interrupt received, shutting down...")
        consumer.stop()
    except Exception as e:
        consumer.logger.error(f"Unexpected error in update event consumer: {str(e)}")
        consumer.stop()
    finally:
        await consumer.disconnect()


# Context manager for using the update event consumer
class UpdateEventConsumerContext:
    """
    Context manager for using the update event consumer
    """
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "update-events-consumer-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id

    async def __aenter__(self):
        self.consumer = UpdateEventConsumer(bootstrap_servers=self.bootstrap_servers, group_id=self.group_id)
        await self.consumer.connect()
        return self.consumer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.consumer.disconnect()