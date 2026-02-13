# from fastapi import FastAPI
# from app.api.health import router as health_router
# from app.api.v1.projects import router as projects_router
# from app.api.v1.tags import router as tags_router

# app = FastAPI(title="Portfolio API")

# app.include_router(health_router)
# app.include_router(projects_router, prefix="/api/v1")
# app.include_router(tags_router)

from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
