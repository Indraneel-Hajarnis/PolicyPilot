"""
SQLAlchemy async engine, session factory, and FastAPI dependency.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings
from app.core.logging_config import get_logger

logger = get_logger("db")

# ── Engine ───────────────────────────────────────────────────────────────────

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},  # SQLite-specific
)

# ── Session Factory ──────────────────────────────────────────────────────────

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model ───────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ── Dependency ───────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields an async database session.

    Usage:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Table Creation ───────────────────────────────────────────────────────────

async def create_tables() -> None:
    """Create all tables defined by ORM models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified")


async def dispose_engine() -> None:
    """Dispose of the engine connection pool."""
    await engine.dispose()
    logger.info("Database engine disposed")
