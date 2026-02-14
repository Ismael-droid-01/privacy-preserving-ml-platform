import os
import shutil
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    directories = [settings.RAW_DATA_PATH, settings.PROCESSED_DATA_PATH]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"TEMP: Subdirectorio creado en {directory}")
    yield

    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)
        print(f"TEMP: Directorio raíz {settings.UPLOAD_DIR} eliminado.")

app = FastAPI(
    title="Preprocess Server",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1") 