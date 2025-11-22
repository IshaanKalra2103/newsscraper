"""Main FastAPI application for News Scraper API."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
from app.database.db import init_db
from app.api.routes import router

# Initialize database
init_db()

# Create FastAPI app with explicit JSON configuration
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=JSONResponse  # Explicit JSON response
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["news"])


# Custom exception handlers to ensure JSON responses
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with JSON response."""
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "message": "Validation error",
            "details": exc.errors(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with JSON response."""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint - returns JSON."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "format": "JSON",
        "docs": "/docs",
        "api": "/api/v1",
        "endpoints": {
            "health": "/health",
            "sources": "/api/v1/sources",
            "scrape": "/api/v1/scrape",
            "articles": "/api/v1/articles",
            "stats": "/api/v1/stats"
        }
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint - returns JSON."""
    return {
        "status": "healthy",
        "format": "JSON",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
