from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import get_logger
from app.api.v1 import health
from app.api.v1 import translation  # <--- Correct import name

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    application.include_router(health.router, prefix="/api/v1", tags=["Health"])
    application.include_router(translation.router, prefix="/api/v1", tags=["Translation"])

    return application

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)