"""NAS Storage & RAG API (FastAPI)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db.session import engine
from app.routers import health, rag, storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="NAS Storage API",
    description="Internal storage and RAG search service for NAS Cloud",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(storage.router, prefix="/storage", tags=["storage"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])
