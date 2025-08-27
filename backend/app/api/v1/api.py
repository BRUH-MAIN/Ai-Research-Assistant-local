"""
Main API router that combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1 import chat, system, sync
from app.api.v1 import users, groups, messages, sessions, feedback

api_router = APIRouter()

# Include routers
api_router.include_router(system.router, tags=["system"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
