from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Create async database engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,           # Set to True to see generated SQL queries (for debugging)
    pool_pre_ping=True    # Checks if connections are still alive
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to get a database session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
