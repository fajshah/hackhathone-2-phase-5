"""
Error handling and retry logic for database operations and other services.
Implements robust error handling with exponential backoff retry mechanism.
"""
import asyncio
import functools
import logging
from typing import Callable, TypeVar, Awaitable, Any, Optional
from datetime import datetime
import random
from sqlalchemy.exc import SQLAlchemyError
from ..models.task import Task


T = TypeVar('T')


class RetryConfig:
    """
    Configuration for retry mechanism
    """
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,  # seconds
        max_delay: float = 60.0,  # seconds
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def retry_on_exception(config: RetryConfig = None):
    """
    Decorator to retry a function on specific exceptions.
    Implements exponential backoff with optional jitter.
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (SQLAlchemyError, ConnectionError, TimeoutError) as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        # Last attempt, raise the exception
                        logging.error(f"All retry attempts failed for {func.__name__}. Last error: {str(e)}")
                        raise e

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    # Add jitter if enabled
                    if config.jitter:
                        delay *= (0.5 + random.random() * 0.5)

                    logging.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )

                    await asyncio.sleep(delay)

            # This line should never be reached due to the return in the loop,
            # but included for type checking
            raise last_exception

        return wrapper
    return decorator


class DatabaseErrorHandler:
    """
    Handler for database-specific error handling and retries
    """

    @staticmethod
    def handle_database_error(error: Exception, operation: str = "unknown"):
        """
        Log and categorize database errors for appropriate handling
        """
        error_msg = f"Database error during {operation}: {str(error)}"

        if isinstance(error, SQLAlchemyError):
            logging.error(f"{error_msg} (SQLAlchemyError)")
            # Could add specific handling for different SQLAlchemy errors here
        elif isinstance(error, ConnectionError):
            logging.error(f"{error_msg} (ConnectionError)")
        elif isinstance(error, TimeoutError):
            logging.error(f"{error_msg} (TimeoutError)")
        else:
            logging.error(f"{error_msg} (Unknown error type)")

        # Raise the original error to be handled by retry mechanism or caller
        raise error

    @staticmethod
    async def safe_execute_with_retry(
        operation: Callable[..., Awaitable[T]],
        *args,
        config: RetryConfig = None,
        **kwargs
    ) -> T:
        """
        Safely execute a database operation with retry logic
        """
        if config is None:
            config = RetryConfig()

        # Wrap the operation with retry decorator
        retry_wrapper = retry_on_exception(config)(operation)
        return await retry_wrapper(*args, **kwargs)


class TaskOperationErrorHandler:
    """
    Specific error handler for task operations
    """

    @staticmethod
    async def handle_create_task_error(error: Exception, task_data: dict) -> Exception:
        """
        Handle errors during task creation
        """
        error_msg = f"Failed to create task with data: {task_data.get('title', 'unknown')}. Error: {str(error)}"
        logging.error(error_msg)

        # Log additional context based on error type
        if isinstance(error, ValueError):
            logging.error("Validation error during task creation")
        elif isinstance(error, SQLAlchemyError):
            logging.error("Database error during task creation")

        return error

    @staticmethod
    async def handle_update_task_error(error: Exception, task_id: str, update_data: dict) -> Exception:
        """
        Handle errors during task update
        """
        error_msg = f"Failed to update task {task_id} with data: {update_data}. Error: {str(error)}"
        logging.error(error_msg)

        if isinstance(error, ValueError):
            logging.error("Validation error during task update")
        elif isinstance(error, SQLAlchemyError):
            logging.error("Database error during task update")

        return error

    @staticmethod
    async def handle_delete_task_error(error: Exception, task_id: str) -> Exception:
        """
        Handle errors during task deletion
        """
        error_msg = f"Failed to delete task {task_id}. Error: {str(error)}"
        logging.error(error_msg)

        if isinstance(error, SQLAlchemyError):
            logging.error("Database error during task deletion")

        return error


# Generic retry utility functions
async def retry_with_backoff(
    operation: Callable[[], Awaitable[T]],
    config: RetryConfig = None,
    is_retryable: Optional[Callable[[Exception], bool]] = None
) -> T:
    """
    Generic retry function with backoff strategy

    Args:
        operation: The async function to retry
        config: Retry configuration
        is_retryable: Function to determine if an exception is retryable
    """
    if config is None:
        config = RetryConfig()

    if is_retryable is None:
        def is_retryable_default(error):
            return isinstance(error, (SQLAlchemyError, ConnectionError, TimeoutError))
        is_retryable = is_retryable_default

    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return await operation()
        except Exception as e:
            last_exception = e

            if not is_retryable(e):
                # Not a retryable error, raise immediately
                raise e

            if attempt == config.max_attempts - 1:
                # Last attempt, raise the exception
                logging.error(f"All retry attempts failed. Last error: {str(e)}")
                raise e

            # Calculate delay with exponential backoff
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )

            # Add jitter if enabled
            if config.jitter:
                delay *= (0.5 + random.random() * 0.5)

            logging.warning(
                f"Attempt {attempt + 1} failed: {str(e)}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            await asyncio.sleep(delay)

    raise last_exception


# Context manager for database transactions with error handling
class TransactionManager:
    """
    Context manager for database transactions with error handling
    """

    def __init__(self, session, autocommit: bool = True):
        self.session = session
        self.autocommit = autocommit
        self.transaction_active = False

    async def __aenter__(self):
        self.transaction_active = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # An exception occurred, rollback the transaction
            await self.session.rollback()
            logging.error(f"Transaction rolled back due to exception: {exc_val}")
        elif self.autocommit:
            # No exception, commit the transaction
            await self.session.commit()
            logging.info("Transaction committed successfully")

        self.transaction_active = False
        return False  # Don't suppress exceptions