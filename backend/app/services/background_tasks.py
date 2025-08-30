"""
Background tasks for Redis-PostgreSQL synchronization
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
# from app.services.redis_postgres_sync import sync_service

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    if settings.ENABLE_REDIS_SYNC:
        logger.info("Starting Redis-PostgreSQL sync service...")
        
        from app.services.redis_postgres_sync import sync_service
        
        # Start the sync service in the background
        sync_task = asyncio.create_task(sync_service.start_sync_listener())
        
        # Perform initial sync
        try:
            await sync_service.manual_full_sync()
            logger.info("Initial sync completed")
        except Exception as e:
            logger.error(f"Initial sync failed: {e}")
    else:
        logger.info("Redis sync is disabled - using PostgreSQL directly")
        sync_task = None
    
    yield
    
    # Shutdown
    if settings.ENABLE_REDIS_SYNC and sync_task:
        logger.info("Stopping Redis-PostgreSQL sync service...")
        from app.services.redis_postgres_sync import sync_service
        sync_service.stop_sync()
        
        # Cancel the sync task
        if not sync_task.done():
            sync_task.cancel()
            try:
                await sync_task
            except asyncio.CancelledError:
                logger.info("Sync task cancelled successfully")
    else:
        logger.info("Application shutdown complete")
