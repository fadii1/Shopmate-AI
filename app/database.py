import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger("KhareedDB")

Base = declarative_base()

# Primary database URL (PostgreSQL default, or configured URL)
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

try:
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True
    )
except Exception as e:
    logger.warning(f"Failed to create engine with {db_url}: {e}. Falling back to SQLite.")
    engine = create_async_engine("sqlite+aiosqlite:///./khareed.db", echo=False, future=True)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initializes all database tables in PostgreSQL (users, carts, orders, alerts, budgets, wishlist)."""
    global engine, async_session_factory
    # Import all models to ensure metadata is populated
    import app.models

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"✅ Database initialized successfully on {engine.url.drivername} ({engine.url.database})")
    except Exception as e:
        print(f"⚠️ Database connection notice: {e}")
        # If PostgreSQL auth failed or db doesn't exist, fallback to local SQLite for seamless operation
        if "sqlite" not in str(engine.url):
            print("Switching engine to SQLite (sqlite+aiosqlite:///./khareed.db) for zero-downtime operation.")
            engine = create_async_engine("sqlite+aiosqlite:///./khareed.db", echo=False, future=True)
            async_session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ SQLite database initialized.")
