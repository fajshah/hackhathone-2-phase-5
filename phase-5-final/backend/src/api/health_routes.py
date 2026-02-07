"""
Health check API routes for the todo chatbot system.
Provides endpoints to verify service availability and dependencies.
"""
from fastapi import APIRouter
from typing import Dict
from datetime import datetime
import time
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import engine


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", status_code=200)
async def health_check() -> Dict:
    """
    Comprehensive health check endpoint.

    Returns service status and dependency health.
    """
    # Check if we can connect to the database
    db_healthy = await check_database_health()

    # Prepare health response
    health_status = {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            },
            "api": {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    }

    status_code = 200 if db_healthy else 503
    return health_status


@router.get("/ready", status_code=200)
async def readiness_check() -> Dict:
    """
    Readiness check to indicate if the service is ready to accept traffic.
    """
    # In a real system, this would check if all initialization is complete
    # For now, we assume the service is ready if it can respond to this endpoint
    # and the database is accessible

    db_ready = await check_database_health()

    ready_status = {
        "status": "ready" if db_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "database": {
                "status": "ready" if db_ready else "not_ready",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    }

    status_code = 200 if db_ready else 503
    return ready_status


@router.get("/live", status_code=200)
async def liveness_check() -> Dict:
    """
    Liveness check to indicate if the service is alive and responding.
    """
    # For liveness, we just check if the service can respond
    # In a more complex service, this might check if the main service loops are running
    liveness_status = {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "todo-chatbot-backend"
    }

    return liveness_status


async def check_database_health() -> bool:
    """
    Check if the database is accessible and responsive.

    Returns:
        True if database is healthy, False otherwise
    """
    try:
        # Create a temporary connection to test database connectivity
        async with engine.begin() as conn:
            # Execute a simple query to test the connection
            result = await conn.execute("SELECT 1")
            row = result.fetchone()

            if row is not None:
                logger.debug("Database health check passed")
                return True
            else:
                logger.error("Database health check failed: SELECT 1 returned no rows")
                return False

    except Exception as e:
        logger.error(f"Database health check failed with error: {str(e)}")
        return False


@router.get("/metrics", status_code=200)
async def get_metrics() -> Dict:
    """
    Metrics endpoint to provide system metrics.
    This is a basic implementation; in a real system you'd integrate with a metrics system like Prometheus.
    """
    import psutil
    import os

    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    # Get process metrics
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info().rss

    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_total": memory_info.total,
            "memory_available": memory_info.available,
            "memory_percent_used": memory_info.percent,
            "disk_total": disk_usage.total,
            "disk_used": disk_usage.used,
            "disk_percent_used": disk_usage.percent
        },
        "process": {
            "memory_rss_bytes": process_memory,
            "num_threads": process.num_threads(),
            "pid": process.pid
        },
        "app": {
            "uptime_seconds": time.time() - getattr(router, '_startup_time', time.time()),
            "version": "1.0.0"
        }
    }

    # Set the startup time if not already set
    if not hasattr(router, '_startup_time'):
        router._startup_time = time.time()

    return metrics