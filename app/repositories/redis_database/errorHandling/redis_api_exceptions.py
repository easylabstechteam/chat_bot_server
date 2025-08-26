# ------------------- IMPORTS -------------------
import logging
from fastapi import HTTPException
from redis.exceptions import RedisError

# ------------------- LOGGER -------------------
# Initialize a logger specifically for exceptions
# This helps track errors related to Redis and other operations
logger = logging.getLogger("chat_data_logger")


# ------------------- REDIS & GENERAL EXCEPTIONS -------------------
class RedisAPIException:

    # Helper class to handle exceptions consistently across Redis operations
    # and other unexpected errors.

    # Provides static methods to:
    # - Log the error
    # - Raise a standardized FastAPI HTTPException

    # -------- HANDLE REDIS ERRORS --------
    @staticmethod
    def handle_redis_error(e: RedisError, message: str = "Redis operation failed"):
        # Log the full Redis exception for debugging
        logger.exception(f"{message}: {e}")

        # Raise HTTP 503 so API consumers know Redis is unavailable
        raise HTTPException(status_code=503, detail=f"{message}: {str(e)}")

    # -------- HANDLE UNEXPECTED ERRORS --------
    @staticmethod
    def handle_unexpected_error(
        e: Exception, message: str = "Unexpected error occurred"
    ):
        # Log the full unexpected exception for debugging
        logger.exception(f"{message}: {e}")

        # Raise HTTP 500 so API consumers know something went wrong on the server
        raise HTTPException(status_code=500, detail=f"{message}: {str(e)}")
