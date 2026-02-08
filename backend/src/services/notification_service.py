"""
Notification service for the todo chatbot system.
Handles sending reminder notifications through various channels.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class NotificationMethod(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in-app"


class NotificationChannel:
    """
    Base class for notification channels
    """
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"NotificationService.{name}")

    async def send_notification(self, recipient: str, message: str, **kwargs) -> bool:
        """
        Send a notification to the recipient.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement send_notification")


class EmailChannel(NotificationChannel):
    """
    Email notification channel
    """
    def __init__(self, smtp_server: str = None, smtp_port: int = None, username: str = None, password: str = None):
        super().__init__("email")
        self.smtp_server = smtp_server or "localhost"
        self.smtp_port = smtp_port or 587
        self.username = username
        self.password = password

    async def send_notification(self, recipient: str, message: str, subject: str = "Todo Chatbot Reminder") -> bool:
        """
        Send an email notification.
        """
        try:
            # In a real implementation, we would use an SMTP client to send the email
            # For now, we'll just log the notification
            self.logger.info(f"Sending email to {recipient}: Subject={subject}, Message={message}")

            # Simulate email sending delay
            await asyncio.sleep(0.1)

            return True
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False


class PushChannel(NotificationChannel):
    """
    Push notification channel
    """
    def __init__(self, service_provider: str = "generic"):
        super().__init__("push")
        self.service_provider = service_provider

    async def send_notification(self, recipient: str, message: str, title: str = "Todo Chatbot Reminder") -> bool:
        """
        Send a push notification.
        """
        try:
            # In a real implementation, we would use a push notification service
            # like Firebase Cloud Messaging, Apple Push Notification Service, etc.
            # For now, we'll just log the notification
            self.logger.info(f"Sending push notification to {recipient}: Title={title}, Message={message}")

            # Simulate push notification delay
            await asyncio.sleep(0.1)

            return True
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {str(e)}")
            return False


class SMSChannel(NotificationChannel):
    """
    SMS notification channel
    """
    def __init__(self, service_provider: str = "twilio"):
        super().__init__("sms")
        self.service_provider = service_provider

    async def send_notification(self, recipient: str, message: str) -> bool:
        """
        Send an SMS notification.
        """
        try:
            # In a real implementation, we would use an SMS service provider
            # like Twilio, AWS SNS, etc.
            # For now, we'll just log the notification
            self.logger.info(f"Sending SMS to {recipient}: Message={message}")

            # Simulate SMS sending delay
            await asyncio.sleep(0.1)

            return True
        except Exception as e:
            self.logger.error(f"Failed to send SMS notification: {str(e)}")
            return False


class InAppChannel(NotificationChannel):
    """
    In-app notification channel
    """
    def __init__(self):
        super().__init__("in_app")

    async def send_notification(self, recipient: str, message: str, task_id: str = None) -> bool:
        """
        Send an in-app notification.
        """
        try:
            # In a real implementation, we would store the notification in the database
            # or send it through WebSocket to the user's session
            # For now, we'll just log the notification
            self.logger.info(f"Sending in-app notification to {recipient}: Message={message}, Task ID={task_id}")

            # Simulate in-app notification delay
            await asyncio.sleep(0.05)

            return True
        except Exception as e:
            self.logger.error(f"Failed to send in-app notification: {str(e)}")
            return False


class NotificationService:
    """
    Service class for sending notifications through various channels
    """
    def __init__(self):
        self.channels: Dict[NotificationMethod, NotificationChannel] = {}
        self.logger = logging.getLogger(__name__)

        # Initialize default channels
        self._initialize_channels()

    def _initialize_channels(self):
        """
        Initialize the notification channels.
        """
        self.channels[NotificationMethod.EMAIL] = EmailChannel()
        self.channels[NotificationMethod.PUSH] = PushChannel()
        self.channels[NotificationMethod.SMS] = SMSChannel()
        self.channels[NotificationMethod.IN_APP] = InAppChannel()

    async def send_notification(self, method: NotificationMethod, recipient: str, message: str, **kwargs) -> bool:
        """
        Send a notification using the specified method.

        Args:
            method: The notification method to use
            recipient: The recipient of the notification
            message: The message to send
            **kwargs: Additional method-specific parameters

        Returns:
            True if the notification was sent successfully, False otherwise
        """
        if method not in self.channels:
            self.logger.error(f"Unsupported notification method: {method}")
            return False

        try:
            channel = self.channels[method]
            success = await channel.send_notification(recipient, message, **kwargs)

            if success:
                self.logger.info(f"Notification sent successfully via {method} to {recipient}")
            else:
                self.logger.error(f"Failed to send notification via {method} to {recipient}")

            return success
        except Exception as e:
            self.logger.error(f"Error sending notification via {method} to {recipient}: {str(e)}")
            return False

    async def send_reminder_notification(self, reminder: Dict[str, Any]) -> bool:
        """
        Send a reminder notification based on reminder data.

        Args:
            reminder: Dictionary containing reminder information

        Returns:
            True if the notification was sent successfully, False otherwise
        """
        try:
            # Extract information from reminder
            recipient = reminder.get('user_id', '')
            message = f"Reminder: {reminder.get('task_title', 'Your task')} is due soon!"
            method = NotificationMethod(reminder.get('method', 'in-app'))

            # Customize message based on the task
            if 'task_title' in reminder:
                message = f"Don't forget: {reminder['task_title']}"

            if 'scheduled_time' in reminder:
                from datetime import datetime
                scheduled_time = reminder['scheduled_time']
                if isinstance(scheduled_time, str):
                    scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                message += f" (scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')})"

            # Send the notification
            success = await self.send_notification(method, recipient, message)

            if success:
                self.logger.info(f"Reminder notification sent for task {reminder.get('task_id')} to user {recipient}")
            else:
                self.logger.error(f"Failed to send reminder notification for task {reminder.get('task_id')} to user {recipient}")

            return success
        except Exception as e:
            self.logger.error(f"Error sending reminder notification: {str(e)}")
            return False

    async def send_multiple_notifications(self, notifications: List[Dict[str, Any]]) -> List[bool]:
        """
        Send multiple notifications concurrently.

        Args:
            notifications: List of notification dictionaries with method, recipient, message, and kwargs

        Returns:
            List of boolean values indicating success/failure for each notification
        """
        tasks = []

        for notification in notifications:
            method = notification.get('method')
            recipient = notification.get('recipient')
            message = notification.get('message')
            kwargs = notification.get('kwargs', {})

            if method and recipient and message:
                task = self.send_notification(NotificationMethod(method), recipient, message, **kwargs)
                tasks.append(task)
            else:
                tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Add a dummy task that returns False
                self.logger.warning(f"Skipping invalid notification: {notification}")

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to False values
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Notification task failed: {str(result)}")
                processed_results.append(False)
            else:
                processed_results.append(result)

        return processed_results

    async def add_channel(self, method: NotificationMethod, channel: NotificationChannel):
        """
        Add a new notification channel.

        Args:
            method: The notification method
            channel: The notification channel to add
        """
        self.channels[method] = channel
        self.logger.info(f"Added notification channel for method: {method}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the notification service.

        Returns:
            Dictionary containing health status information
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "channels": {}
        }

        # Check each channel
        for method, channel in self.channels.items():
            # For now, just check if the channel exists and has the required methods
            channel_status = {
                "status": "available",
                "name": channel.name
            }

            health_status["channels"][method.value] = channel_status

        return health_status


# Global instance of the Notification Service
_notification_service: Optional[NotificationService] = None


async def get_notification_service() -> NotificationService:
    """
    Get the singleton instance of the Notification Service.
    """
    global _notification_service

    if _notification_service is None:
        _notification_service = NotificationService()

    return _notification_service


# Context manager for using the notification service
class NotificationServiceContext:
    """
    Context manager for using the notification service.
    """
    def __init__(self):
        pass

    async def __aenter__(self):
        self.service = await get_notification_service()
        return self.service

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup operations if needed
        pass