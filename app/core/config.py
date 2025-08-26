import os
from dotenv import load_dotenv

# ------------------- LOAD ENVIRONMENT VARIABLES -------------------
# Load variables from a .env file into the OS environment
# This keeps secrets like API keys, database URLs, and ports out of the code
load_dotenv()

# ------------------- REDIS CONFIGURATION -------------------
# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")           # Redis server host (default: localhost)
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))            # Redis port (default: 6379)
REDIS_DB = int(os.getenv("REDIS_DB", 0))                   # Redis database index (default: 0)
REDIS_EXPIRE_SECONDS = int(os.getenv("REDIS_EXPIRE_SECONDS", 86400))  # Expire keys after 1 day

# ------------------- POSTGRESQL CONFIGURATION -------------------
# Async SQLAlchemy connection string for PostgreSQL
# Default is for local development; in production, set DATABASE_URL in environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/chatbot_db"
)

# ------------------- LANGCHAIN / GOOGLE GEMINI CONFIGURATION -------------------
# API key for Google Generative AI (Gemini)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model name for Gemini; configurable or uses default
GENIE_MODEL_NAME = os.getenv("GENIE_MODEL_NAME", "gemini-2.5-flash")

# ------------------- NOTES -------------------
# - All configuration is loaded from environment variables for security and flexibility
# - Redis settings define connection and key expiration behavior
# - DATABASE_URL must be configured for production to connect to PostgreSQL
# - GOOGLE_API_KEY and GENIE_MODEL_NAME configure the LLM client
# - Additional LLM or LangChain-specific configurations can be added here
