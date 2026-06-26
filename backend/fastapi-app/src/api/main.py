from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncpg
from src.shared.core.database import get_db_session, init_pool, close_pool
from src.shared.common.logging.log import get_logger
from src.api.routers import auth_router, organizer_router, dashboard_router, member_router, chit_group_router
from src.api.routers import chit_auction_router, chit_collection_router, winner_payout_router, member_portal_router, financial_summary_router
from src.shared.common.exceptions import AppError

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application and initializing database pool...")
    await init_pool()
    yield
    # Shutdown
    logger.info("Shutting down application and closing database pool...")
    await close_pool()

app = FastAPI(
    title="Chit Fund Management System API",
    description="Backend services for Chit Fund Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend origin
import os
origins_env = os.getenv("ALLOWED_ORIGINS", "")
if origins_env:
    origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
else:
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router)
app.include_router(organizer_router.router)
app.include_router(dashboard_router.router)
app.include_router(member_router.router)
app.include_router(chit_group_router.router)
app.include_router(chit_auction_router.router)
app.include_router(chit_collection_router.router)
app.include_router(winner_payout_router.router)
app.include_router(member_portal_router.router)
app.include_router(financial_summary_router.router)


# Register custom exception handler
@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError):
    """
    Global exception handler for all custom AppError exceptions.
    """
    logger.error(f"Application error: status_code={exc.status_code}, message='{exc.message}'")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.message,
            "details": exc.details or {}
        }
    )

@app.get("/health")
async def health_check(db_object: asyncpg.Connection = Depends(get_db_session)):
    """
    Health check endpoint to verify API and Database status.
    """
    try:
        # Perform a simple query to verify database connection
        await db_object.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Health check failed for database: {e}")
        db_status = "unhealthy"

    status = "healthy" if db_status == "healthy" else "unhealthy"
    
    return {
        "status": status,
        "api": "healthy",
        "database": db_status
    }
