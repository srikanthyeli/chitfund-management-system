import asyncpg
from src.shared.core.properties.app_properties import settings

# Global variable for connection pool
async_pg_pool = None

# Initialize connection pool
async def init_pool():
    """
    Initializes the connection pool for PostgreSQL.
    """
    global async_pg_pool
    if async_pg_pool is None:
        async_pg_pool = await asyncpg.create_pool(
            dsn=settings.database.db_url,
            # Keep startup lightweight so transient DB pressure does not fail boot.
            min_size=1,
            max_size=300,  # Increase the maximum pool size for higher concurrency
        )
        print("Database connection pool initialized.")

# Dependency function for database access
async def get_db_session():
    """
    Dependency function to get a database connection from the pool.
    Ensures the connection is released back to the pool after use.
    """
    global async_pg_pool
    if not async_pg_pool:
        raise Exception("Database pool is not initialized. Call 'init_pool()' first.")

    async with async_pg_pool.acquire() as conn:
        try:
            yield conn
        finally:
            # Connection is automatically returned to the pool
            pass

# Shutdown connection pool
async def close_pool():
    """
    Gracefully closes the connection pool during application shutdown.
    """
    global async_pg_pool
    if async_pg_pool:
        await async_pg_pool.close()
        async_pg_pool = None
        print("Database connection pool closed.")
