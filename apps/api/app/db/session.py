"""Database session factory and async session management.

Provides database session creation and dependency injection for FastAPI.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.base import Base

logger = get_logger(__name__)


def get_database_url() -> str:
    """Get database URL from settings.
    
    Returns:
        str: Database URL (SQLite for dev, PostgreSQL for prod)
    """
    settings = get_settings()
    db_url = settings.database_url
    
    # Convert sqlite:// to sqlite+aiosqlite:// for async support
    if db_url.startswith("sqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite:///", 1)
    
    return db_url


# Create async engine
_database_url = get_database_url()
engine = create_async_engine(
    _database_url,
    echo=False,  # Set to True to see SQL queries
    future=True,
    pool_pre_ping=True,  # Verify connections are alive
    connect_args={"check_same_thread": False} if "aiosqlite" in _database_url else {},
)

# Create async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

logger.info(
    "Database engine initialized",
    extra={
        "database_url": _database_url.replace("aiosqlite://", "sqlite://").replace("sqlite+aiosqlite:///", "sqlite:///"),
    },
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for dependency injection.
    
    Usage in FastAPI routes:
        >>> @app.get("/items/")
        >>> async def get_items(db: AsyncSession = Depends(get_db_session)):
        ...     return await db.execute(select(Item))
    
    Yields:
        AsyncSession: Database session
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables() -> None:
    """Create all database tables.
    
    Must be called during application startup.
    
    Example:
        >>> app = create_app()
        >>> @app.on_event("startup")
        >>> async def startup():
        ...     await create_tables()
    """
    logger.info("Creating database tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def drop_tables() -> None:
    """Drop all database tables.
    
    WARNING: Only use in development/testing.
    """
    logger.warning("Dropping all database tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db() -> None:
    """Close database connections.
    
    Must be called during application shutdown.
    
    Example:
        >>> @app.on_event("shutdown")
        >>> async def shutdown():
        ...     await close_db()
    """
    logger.info("Closing database connection")
    await engine.dispose()
