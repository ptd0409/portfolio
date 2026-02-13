# app/api/v1/router.py
from fastapi import APIRouter
from app.modules.projects.router import router as projects_router
from app.modules.tags.router import router as tags_router

api_router = APIRouter()

api_router.include_router(projects_router)
api_router.include_router(tags_router)
