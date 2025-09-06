from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base

DATABASE_URL = "postgresql+asyncpg://chatbot_user:chatbot_pass@postgres:5432/chatbot_db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

async def init_db():
    async with engine.begin() as conn:
        # Drop all tables if needed (for fresh dev start)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables based on your models
        await conn.run_sync(Base.metadata.create_all)
