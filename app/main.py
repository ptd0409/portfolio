from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.v1.projects import router as projects_router

app = FastAPI(title="Portfolio API")

app.include_router(health_router)
app.include_router(projects_router, prefix="/api/v1")