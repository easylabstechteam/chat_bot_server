import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_EXPIRE_SECONDS = int(os.getenv("REDIS_EXPIRE_SECONDS", 86400))

# Postgres async engine
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://chatbot_user:chatbot_pass@postgres:5432/chatbot_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)

# Async session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base model
Base = declarative_base()

# Optional: dev helper to create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# LangChain / Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GENIE_MODEL_NAME = os.getenv("GENIE_MODEL_NAME", "gemini-2.5-flash")
