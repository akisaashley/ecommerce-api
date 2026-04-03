from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.mysql_connector import get_pool_status, ping_database
from app.middleware.logging import log_json

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    db_ok = ping_database()
    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    log_json(
        "info",
        "health_check",
        database_status="up" if db_ok else "down",
        app_name=settings.APP_NAME,
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "success": db_ok,
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "database": "up" if db_ok else "down",
            "pool": get_pool_status(),
            "developer": "Akisa Ashley Maria",
            "student_id": "2300705729",
        },
    )