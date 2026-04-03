from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import initialize_database
from app.database.mysql_connector import get_pool_status, init_connection_pool, ping_database
from app.middleware.logging import RequestLoggingMiddleware, app_logger, configure_logging, log_json
from app.routes import health_router, products_router, orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.LOG_LEVEL)
    init_connection_pool()
    initialize_database()

    log_json(
        "info",
        "application_startup",
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        developer="Akisa Ashley Maria",
        student_id="2300705729",
    )
    yield
    log_json("info", "application_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    description="""
    E-Commerce API - Production Ready
    Developer: Akisa Ashley Maria (2300705729)
    Makerere University - Software Engineering
    
    Features:
    - Product management with stock tracking
    - Order processing with transaction support
    - Inventory transaction logging
    - Automatic database seeding
    """,
)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(health_router)
app.include_router(products_router)
app.include_router(orders_router)


@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "E-Commerce API",
        "version": "1.0.0",
        "developer": "Akisa Ashley Maria",
        "student_id": "2300705729",
        "institution": "Makerere University",
        "endpoints": {
            "health": "/health",
            "products": "/api/products",
            "orders": "/api/orders",
            "docs": "/docs",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_logger.exception(
        {
            "event": "unhandled_exception",
            "path": str(request.url.path),
            "method": request.method,
            "request_id": getattr(request.state, "request_id", "-"),
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", "-"),
        },
    )