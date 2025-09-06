import os
from dotenv import load_dotenv


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
    "postgresql+asyncpg://chatbot_user:chatbot_pass@postgres:5433/chatbot_db"
)
# LangChain / Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GENIE_MODEL_NAME = os.getenv("GENIE_MODEL_NAME", "gemini-2.5-flash")
