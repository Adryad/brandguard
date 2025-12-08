import uuid
from datetime import datetime
from fastapi import HTTPException
# brandguard/backend/app/main.py (Updated with requirements dependencies)
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, es_client, get_db, redis_client

# Configure structured logging (from requirements.txt)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger("brandguard.main")


class BrandGuardApp:
    """BrandGuard FastAPI application with requirements integration"""

    def __init__(self):
        self.app = FastAPI(
            title=settings.PROJECT_NAME,
            version="1.0.0",
            description="BrandGuard - Company Reputation Analysis Platform with AI",
            lifespan=self.lifespan,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_tags=[
                {"name": "companies", "description": "Company management operations"},
                {"name": "analysis", "description": "Real-time analysis services"},
                {"name": "alerts", "description": "Smart alerting systems"},
                {"name": "reports", "description": "Data export functionality"},
                {"name": "health", "description": "System health monitoring"},
            ],
        )

        self.setup_middleware()
        self.setup_instrumentation()
        self.setup_routes()

    def setup_middleware(self):
        """Configure all middleware from requirements"""

        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "https://brandguard.app"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=86400,
        )

        # Compression middleware (from starlette)
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Request ID middleware (from starlette)
        @self.app.middleware("http")
        async def add_request_id(request: Request, call_next):
            request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

    def setup_instrumentation(self):
        """Setup Prometheus metrics instrumentation"""
        Instrumentator(
            should_group_requests=False,
            should_group_untemplated=True,
        ).instrument(self.app).expose(self.app, should_gzip=True)

    def setup_routes(self):
        """Setup API routes and error handlers"""
        # Include API router
        self.app.include_router(api_router, prefix=settings.API_V1_STR)

        # Health check
        @self.app.get("/health", tags=["health"])
        async def health_check():
            """Health check endpoint with dependencies validation"""
            try:
                # Check database
                db = next(get_db())
                db.execute("SELECT 1")

                # Check Redis
                redis = get_redis()
                redis.ping()

                # Check Elasticsearch
                es = get_elasticsearch()
                es.ping()

                return {
                    "status": "healthy",
                    "service": settings.PROJECT_NAME,
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "checks": {
                        "database": "pass",
                        "redis": "pass",
                        "elasticsearch": "pass",
                    },
                }
            except Exception as e:
                logger.error("Health check failed", error=str(e))
                return JSONResponse(
                    status_code=503, content={"status": "unhealthy", "error": str(e)}
                )

        # Error handlers
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            """Global exception handler with proper logging"""
            status_code = 500
            if isinstance(exc, HTTPException):
                status_code = exc.status_code

            request_id = request.headers.get("X-Request-ID", "unknown")
            logger.error(
                "Unhandled exception",
                error=str(exc),
                request_id=request_id,
                url=str(request.url),
                method=request.method,
            )

            return JSONResponse(
                status_code=status_code,
                content={"detail": "Internal server error", "request_id": request_id},
            )

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage application lifecycle with proper initialization"""
        logger.info("Starting BrandGuard Application with all dependencies...")

        # Initialize database
        Base.metadata.create_all(bind=engine)

        # Test external services
        try:
            redis_client.ping()
            es_client.ping()
            logger.info("External services connected successfully")
        except Exception as e:
            logger.warning("Some external services unavailable", error=str(e))

        yield

        logger.info("Shutting down BrandGuard Application...")


# Create global app instance
brandguarded_app = BrandGuardApp().app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:brandguarded_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        use_colors=True,
    )
