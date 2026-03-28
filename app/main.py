"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.core.settings import get_settings
from app.core.exceptions import AppError
from app.db.database import init_db, get_db
from app.utils.logger import setup_logging, get_logger
from app.api import routes, tasks, grader, baseline
from app.services.kb_service import KBService
from app.rag.vector_store import get_vector_store

settings = get_settings()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup.begin", version=settings.APP_VERSION)
    await init_db()

    # Seed KB and build FAISS index
    async for db in get_db():
        kb_svc = KBService(db)
        count  = await kb_svc.seed()
        logger.info("startup.kb_ready", documents=count)

    # Try to load existing FAISS index
    vs = get_vector_store()
    if not vs.load():
        logger.warning("startup.faiss_no_index_found — will rebuild on next seed")

    logger.info("startup.complete")
    yield
    logger.info("shutdown.complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="OpenEnv-compliant AI Customer Support Resolution Environment",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "message": exc.message},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc), path=str(request.url))
    return JSONResponse(status_code=500, content={"error": "InternalServerError", "message": str(exc)})


# Register routers
app.include_router(routes.router)
app.include_router(tasks.router)
app.include_router(grader.router)
app.include_router(baseline.router)

# Serve frontend UI
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/ui", StaticFiles(directory=_frontend_dir, html=True), name="frontend")


@app.get("/ui", include_in_schema=False)
async def serve_ui():
    return FileResponse(os.path.join(_frontend_dir, "index.html"))


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/", tags=["Health"])
async def root():
    return {
        "name":    settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs":    "/docs",
    }
