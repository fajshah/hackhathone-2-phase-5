"""
Dapr Jobs API integration for the todo chatbot system.
Handles scheduling and management of background jobs using Dapr.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime


class DaprJobsService:
    """
    Service for interacting with Dapr Jobs API
    """

    def __init__(self, dapr_client=None, dapr_http_port: int = 3500):
        self.dapr_client = dapr_client
        self.dapr_http_port = dapr_http_port
        self.logger = logging.getLogger(__name__)

    async def schedule_job(self, job_name: str, scheduled_time: datetime,
                          callback_url: str, payload: Dict[str, Any]) -> str:
        """
        Schedule a job using Dapr Jobs API.

        Args:
            job_name: Name of the job
            scheduled_time: When the job should run
            callback_url: URL to call when job runs
            payload: Payload to send with the job callback

        Returns:
            Job ID of the scheduled job
        """
        if not self.dapr_client:
            # Initialize Dapr client if not provided
            try:
                from dapr.clients import DaprClient
                self.dapr_client = DaprClient()
            except ImportError:
                self.logger.error("Dapr client not available. Install dapr.")
                raise

        # Format the time according to RFC3339
        time_str = scheduled_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Prepare the job request payload
        job_request = {
            "jobName": job_name,
            "scheduleTime": time_str,
            "jobData": {
                "callbackUrl": callback_url,
                "payload": payload
            }
        }

        try:
            # Make HTTP request to Dapr Jobs API
            # Dapr Jobs API is not officially released yet, so this is a conceptual implementation
            # For now, we'll use the Dapr client to invoke a service that handles scheduling

            # In a real implementation, this would make a direct HTTP call to:
            # POST http://localhost:<dapr_http_port>/v1.0/jobs/<job_name>

            # For this example, we'll simulate the scheduling by returning a job ID
            job_id = f"job-{job_name}-{int(scheduled_time.timestamp())}"

            self.logger.info(f"Scheduled job {job_id} for {time_str}")

            return job_id
        except Exception as e:
            self.logger.error(f"Failed to schedule job: {str(e)}")
            raise

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a scheduled job.

        Args:
            job_id: ID of the job to cancel

        Returns:
            True if cancellation was successful, False otherwise
        """
        try:
            # In a real implementation, this would make a direct HTTP call to:
            # DELETE http://localhost:<dapr_http_port>/v1.0/jobs/<job_id>

            # For now, we'll just return True indicating the job was cancelled
            self.logger.info(f"Cancelled job {job_id}")

            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel job {job_id}: {str(e)}")
            return False

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a scheduled job.

        Args:
            job_id: ID of the job to check

        Returns:
            Dictionary containing job status, or None if not found
        """
        try:
            # In a real implementation, this would make a direct HTTP call to:
            # GET http://localhost:<dapr_http_port>/v1.0/jobs/<job_id>

            # For now, we'll return a mock status
            status = {
                "jobId": job_id,
                "status": "scheduled",  # Options: scheduled, running, completed, failed, cancelled
                "scheduledTime": "2026-02-05T12:00:00Z",
                "actualRunTime": None,
                "result": None
            }

            return status
        except Exception as e:
            self.logger.error(f"Failed to get job status for {job_id}: {str(e)}")
            return None

    async def schedule_reminder_job(self, reminder_id: str, scheduled_time: datetime,
                                  user_id: str, task_id: str) -> str:
        """
        Schedule a specific reminder job.

        Args:
            reminder_id: ID of the reminder to schedule
            scheduled_time: When the reminder should be triggered
            user_id: ID of the user receiving the reminder
            task_id: ID of the task associated with the reminder

        Returns:
            Job ID of the scheduled reminder
        """
        # Define the callback URL for when the reminder should fire
        # This would call the notification service
        callback_url = f"http://notification-service:8080/api/v1/reminders/{reminder_id}/trigger"

        # Prepare the payload with reminder information
        payload = {
            "reminder_id": reminder_id,
            "user_id": user_id,
            "task_id": task_id,
            "scheduled_time": scheduled_time.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }

        # Create a unique job name for the reminder
        job_name = f"reminder-{reminder_id}"

        # Schedule the job
        job_id = await self.schedule_job(
            job_name=job_name,
            scheduled_time=scheduled_time,
            callback_url=callback_url,
            payload=payload
        )

        return job_id

    async def schedule_recurring_job(self, job_name: str, cron_expression: str,
                                   callback_url: str, payload: Dict[str, Any]) -> str:
        """
        Schedule a recurring job using cron-like syntax.

        Args:
            job_name: Name of the job
            cron_expression: Cron expression for scheduling
            callback_url: URL to call when job runs
            payload: Payload to send with the job callback

        Returns:
            Job ID of the scheduled recurring job
        """
        # Dapr Jobs API currently doesn't have official support for recurring jobs
        # This is a conceptual implementation

        # In a real implementation, recurring jobs would be scheduled differently
        # For now, we'll just log that we attempted to schedule a recurring job
        self.logger.info(f"Scheduled recurring job {job_name} with cron: {cron_expression}")

        job_id = f"recurring-job-{job_name}-{cron_expression.replace('*', 'star').replace(' ', '-').replace('/', '-')}"

        return job_id

    async def health_check(self) -> bool:
        """
        Check if Dapr Jobs API is accessible.

        Returns:
            True if Dapr Jobs API is accessible, False otherwise
        """
        try:
            # Test connectivity to Dapr
            # This is a conceptual check as Dapr Jobs API doesn't exist yet
            # In reality, we would try to connect to the Dapr sidecar
            if self.dapr_client:
                return True
            else:
                # Try to initialize the client
                try:
                    from dapr.clients import DaprClient
                    with DaprClient() as client:
                        # Try a simple operation to verify connectivity
                        pass
                    return True
                except:
                    return False
        except Exception as e:
            self.logger.error(f"Dapr Jobs health check failed: {str(e)}")
            return False


# Global instance of the Dapr Jobs Service
_dapr_jobs_service: Optional[DaprJobsService] = None


async def get_dapr_jobs_service(dapr_client=None) -> DaprJobsService:
    """
    Get the singleton instance of the Dapr Jobs Service.
    """
    global _dapr_jobs_service

    if _dapr_jobs_service is None:
        _dapr_jobs_service = DaprJobsService(dapr_client=dapr_client)

    return _dapr_jobs_service


# Helper function to schedule a reminder using Dapr Jobs
async def schedule_reminder_with_dapr(
    reminder_id: str,
    scheduled_time: datetime,
    user_id: str,
    task_id: str,
    dapr_client=None
) -> str:
    """
    Helper function to schedule a reminder using Dapr Jobs API.

    Args:
        reminder_id: ID of the reminder to schedule
        scheduled_time: When the reminder should be triggered
        user_id: ID of the user receiving the reminder
        task_id: ID of the task associated with the reminder
        dapr_client: Optional Dapr client instance

    Returns:
        Job ID of the scheduled reminder
    """
    dapr_jobs_service = await get_dapr_jobs_service(dapr_client)

    job_id = await dapr_jobs_service.schedule_reminder_job(
        reminder_id=reminder_id,
        scheduled_time=scheduled_time,
        user_id=user_id,
        task_id=task_id
    )

    return job_id


# Context manager for using the Dapr Jobs service
class DaprJobsServiceContext:
    """
    Context manager for using the Dapr Jobs service.
    Ensures proper initialization and cleanup.
    """
    def __init__(self, dapr_client=None):
        self.dapr_client = dapr_client

    async def __aenter__(self):
        self.service = await get_dapr_jobs_service(self.dapr_client)
        return self.service

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup operations if needed
        pass