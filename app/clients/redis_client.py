import redis.asyncio as redis  # Async Redis library for Python
from core import config         # Import project configuration (host, port, db, etc.)

# Create an async Redis connection pool
# Using a connection pool improves performance by reusing connections
pool = redis.ConnectionPool(
    host=config.REDIS_HOST,    # Redis server hostname or IP
    port=config.REDIS_PORT,    # Redis server port (default 6379)
    db=config.REDIS_DB,        # Redis database index (0 by default)
    decode_responses=True      # Automatically decode byte responses to Python str
)

# Async Redis client instance using the connection pool
# This client will be used throughout the project for Redis operations
redis_client = redis.Redis(connection_pool=pool)
