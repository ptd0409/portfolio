from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = (BASE_DIR.parent / "uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
