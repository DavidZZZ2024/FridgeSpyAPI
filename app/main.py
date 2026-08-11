import logging
import os

import snowflake.connector
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.routers import metadata, products, statistics
from app.services.snowflake_service import fetch_one


class HomeResponse(BaseModel):
    message: str
    status: str


class HealthResponse(BaseModel):
    status: str


class DatabaseHealthResponse(BaseModel):
    status: str
    snowflake_version: str | None


app = FastAPI(
    title="FridgeSpy API",
    description="Australian refrigerator price intelligence API",
    version="1.0.0",
)
logger = logging.getLogger("fridgespy")

default_frontend_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://fridgespy-web.onrender.com",
]
allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", ",".join(default_frontend_origins)).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_model=HomeResponse)
def home():
    return {"message": "FridgeSpy API is running", "status": "healthy"}


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}


@app.get("/database-health", response_model=DatabaseHealthResponse)
def database_health():
    try:
        row = fetch_one("SELECT CURRENT_VERSION() AS snowflake_version")
        return {"status": "ok", "snowflake_version": row["snowflake_version"] if row else None}
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Snowflake connection check failed")
        raise HTTPException(status_code=503, detail="Database connection unavailable") from exc


app.include_router(products.router)
app.include_router(metadata.router)
app.include_router(statistics.router)
