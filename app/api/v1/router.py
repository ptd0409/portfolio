# app/api/v1/router.py
from fastapi import APIRouter
from app.modules.projects.router import router as projects_router
from app.modules.tags.router import router as tags_router
from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.modules.media.router import router as media_router

api_router = APIRouter()

api_router.include_router(projects_router)
api_router.include_router(tags_router)
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(media_router)
