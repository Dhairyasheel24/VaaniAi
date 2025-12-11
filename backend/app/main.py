# FILE: backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import get_logger
from app.api.v1 import health
from app.api.v1 import translation
from app.api.v1 import audio

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

def create_application() -> FastAPI:
    # Renamed internal variable to 'app'
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(translation.router, prefix="/api/v1", tags=["Translation"])
    app.include_router(audio.router, prefix="/api/v1", tags=["Audio"])

    # Root Redirect to Docs
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    return app

# Global instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)