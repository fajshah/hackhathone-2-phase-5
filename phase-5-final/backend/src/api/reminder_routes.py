"""
Reminder API routes for the todo chatbot system.
Handles scheduling, cancelling, and viewing reminders.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import datetime
from ..models.reminder import Reminder
from ..services.reminder_service import ReminderService
from ..dapr.jobs import schedule_reminder_with_dapr
from .models import ReminderCreateRequest, ReminderResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_session


router = APIRouter()


@router.post("/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_request: ReminderCreateRequest,
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Schedule a new reminder.
    """
    try:
        # Initialize services
        # We would normally have access to the TaskService here as well
        # For this example, we'll pass None to the ReminderService constructor
        reminder_service = ReminderService()

        # Convert request model to dict
        reminder_data = reminder_request.dict()

        # Schedule the reminder
        reminder = await reminder_service.schedule_reminder(reminder_data)

        # Here we would integrate with Dapr Jobs API to actually schedule the reminder
        # In a real implementation:
        # job_id = await schedule_reminder_with_dapr(
        #     reminder_id=reminder.id,
        #     scheduled_time=reminder.scheduled_time,
        #     user_id=reminder.user_id,
        #     task_id=reminder.task_id
        # )

        # Create response model
        return ReminderResponse(
            id=reminder.id,
            task_id=reminder.task_id,
            user_id=reminder.user_id,
            scheduled_time=reminder.scheduled_time,
            status=reminder.status.value,
            method=reminder.method.value,
            created_at=reminder.created_at,
            sent_at=reminder.sent_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reminder: {str(e)}"
        )


@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(
    user_id: str = Query(..., description="User ID to filter reminders"),
    status: str = Query(None, description="Filter by reminder status"),
    limit: int = Query(10, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Get upcoming reminders for a user.
    """
    try:
        # Initialize reminder service
        reminder_service = ReminderService()

        # Get upcoming reminders for the user
        reminders = await reminder_service.get_upcoming_reminders(user_id, limit)

        # Convert to response models
        return [
            ReminderResponse(
                id=reminder.id,
                task_id=reminder.task_id,
                user_id=reminder.user_id,
                scheduled_time=reminder.scheduled_time,
                status=reminder.status.value,
                method=reminder.method.value,
                created_at=reminder.created_at,
                sent_at=reminder.sent_at
            )
            for reminder in reminders
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminders: {str(e)}"
        )


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: str,
    user_id: str = Query(..., description="User ID"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific reminder by ID.
    """
    try:
        # Initialize reminder service
        reminder_service = ReminderService()

        # Get the reminder
        reminder = await reminder_service.get_reminder_by_id(reminder_id, user_id)

        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found or user not authorized"
            )

        return ReminderResponse(
            id=reminder.id,
            task_id=reminder.task_id,
            user_id=reminder.user_id,
            scheduled_time=reminder.scheduled_time,
            status=reminder.status.value,
            method=reminder.method.value,
            created_at=reminder.created_at,
            sent_at=reminder.sent_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reminder: {str(e)}"
        )


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reminder(
    reminder_id: str,
    user_id: str = Query(..., description="User ID"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Cancel a scheduled reminder.
    """
    try:
        # Initialize reminder service
        reminder_service = ReminderService()

        # Cancel the reminder
        reminder = await reminder_service.cancel_reminder(reminder_id, user_id)

        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found or user not authorized"
            )

        # In a real implementation, we would also cancel the Dapr job here
        # dapr_job_id = f"dapr-job-{reminder_id}"
        # await cancel_dapr_job(dapr_job_id)

        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel reminder: {str(e)}"
        )


@router.put("/reminders/{reminder_id}/reschedule", response_model=ReminderResponse)
async def reschedule_reminder(
    reminder_id: str,
    scheduled_time: str = Query(..., description="New scheduled time for the reminder in ISO format"),
    user_id: str = Query(..., description="User ID"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    Reschedule a reminder to a new time.
    """
    try:
        # Initialize reminder service
        reminder_service = ReminderService()

        # Parse the new scheduled time
        new_scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))

        # First get the existing reminder to copy other properties
        existing_reminder = await reminder_service.get_reminder_by_id(reminder_id, user_id)

        if not existing_reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found or user not authorized"
            )

        # Cancel the existing reminder
        cancelled_reminder = await reminder_service.cancel_reminder(reminder_id, user_id)

        if not cancelled_reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not cancel existing reminder"
            )

        # Create new reminder data with updated time
        new_reminder_data = {
            'task_id': existing_reminder.task_id,
            'user_id': existing_reminder.user_id,
            'scheduled_time': new_scheduled_time,
            'method': existing_reminder.method.value,
        }

        # Schedule the new reminder
        new_reminder = await reminder_service.schedule_reminder(new_reminder_data)

        return ReminderResponse(
            id=new_reminder.id,
            task_id=new_reminder.task_id,
            user_id=new_reminder.user_id,
            scheduled_time=new_reminder.scheduled_time,
            status=new_reminder.status.value,
            method=new_reminder.method.value,
            created_at=new_reminder.created_at,
            sent_at=new_reminder.sent_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reschedule reminder: {str(e)}"
        )


# Add the reminder routes to the router
# Note: The actual reminder routes would need to be added to the main app
# in the same way as the task and health routes were added