# ------------------- IMPORTS -------------------
import json  # For converting Python objects to JSON strings
from uuid import UUID, uuid4  # For unique session IDs
from datetime import datetime  # For timestamps

from fastapi import HTTPException  # To raise HTTP errors in FastAPI
from redis.exceptions import RedisError  # To handle Redis-specific errors

from clients.redis_client import redis_client  # Redis client instance

# Pydantic models for input/output validation
from repositories.validations.redis_database.input.create_chat_data_input import (
    CreateChatDataInput,
    RedisSetDataInput,
    CreateChatMessage,
)
from repositories.validations.redis_database.output.create_chat_data_output import (
    CreateChatDataOutput,
)
from repositories.validations.redis_database.input.delete_chat_data_input import (
    DeleteChatDataInput,
)
from repositories.validations.redis_database.output.delete_chat_data_output import (
    DeleteChatDataOutput,
)
from repositories.validations.redis_database.input.get_chat_data_input import (
    GetChatDataInput,
)
from repositories.validations.redis_database.output.get_chat_data_output import (
    GetChatDataOutput,
    Message,
)
from repositories.validations.redis_database.input.update_chat_data_input import (
    UpdateChatDataInput,
)
from repositories.validations.redis_database.output.update_chat_data_output import (
    UpdateChatDataOutput,
)

# Custom exception handler for Redis/unexpected errors
from repositories.redis_database.errorHandling.redis_api_exceptions import RedisAPIException

# Universal logger
from utils.logger_setup import get_logger

# ------------------- LOGGER -------------------
logger = get_logger("chat_data_logger")  # Logger named 'chat_data_logger'


# ------------------- REDIS REPOSITORY -------------------
class RedisRepository:
    
    # Repository class for managing chat sessions in Redis.
    # Provides CRUD operations:
    # - Create a new chat session
    # - Read/fetch existing session
    # - Update existing session
    # - Delete session
  

    # ------------------- CREATE CHAT DATA -------------------
    @staticmethod
    async def create_chat_data(chat_data: CreateChatDataInput) -> CreateChatDataOutput:
        
        # Create a new chat session in Redis with a unique session ID.
        # Stores the first user message in the session.
      
        key = str(uuid4())  # Generate a unique session ID
        chat_data.session_id = key  # Assign session ID to the input object
        logger.info(f"Creating new chat session with ID: {key}")

        try:
            # Create the first message object
            message_obj = CreateChatMessage(
                session_id=chat_data.session_id,
                role="user",
                timestamp=datetime.utcnow(),
                message=chat_data.message,
            )

            # Prepare Redis payload and serialize to JSON
            redis_payload = RedisSetDataInput(
                session_id=chat_data.session_id,
                messages=[message_obj],
            ).model_dump_json()

            # Save session in Redis
            result: bool = await redis_client.set(key, redis_payload)

            if not result:  # Handle failure
                logger.error(f"Failed to save chat data for session {key}")
                raise HTTPException(status_code=500, detail="Failed to save chat data")

            logger.info(f"Chat data saved successfully for session {key}")
            return CreateChatDataOutput(update_status=result, session_id=key)

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while creating chat")
        except Exception as e:
            RedisAPIException.handle_unexpected_error(e, "Unexpected error while creating chat")

    # ------------------- DELETE CHAT DATA -------------------
    @staticmethod
    async def delete_chat_data(session_id: DeleteChatDataInput) -> DeleteChatDataOutput:
      
        # Delete an existing chat session from Redis using its session ID.
      
        key = str(session_id)
        logger.info(f"Deleting chat session {key} from Redis")

        try:
            result: int = await redis_client.delete(key)
            if result == 0:  # Key does not exist
                logger.warning(f"Session {key} not found in Redis")
                raise HTTPException(status_code=404, detail=f"Session {key} does not exist")

            logger.info(f"Session {key} deleted successfully")
            return DeleteChatDataOutput(delete_status=result, session_id=key)

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while deleting chat")
        except Exception as e:
            RedisAPIException.handle_unexpected_error(e, "Unexpected error while deleting chat")

    # ------------------- GET CHAT DATA -------------------
    @staticmethod
    async def get_chat_data(session_id: UUID) -> GetChatDataOutput:
       
        # Fetch all messages of a chat session from Redis.
       
        key = str(session_id)
        logger.info(f"Fetching chat session {key} from Redis")

        try:
            response = await redis_client.get(key)
            if not response:
                logger.warning(f"Session {key} not found in Redis")
                raise HTTPException(status_code=404, detail=f"Session {key} not found")

            chat_dict = json.loads(response)
            return GetChatDataOutput(session_id=session_id, messages=chat_dict.get("messages"))

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while fetching chat")
        except Exception as e:
            RedisAPIException.handle_unexpected_error(e, "Unexpected error while fetching chat")

    # ------------------- UPDATE CHAT DATA -------------------
    @staticmethod
    async def update_chat_data(chat_data: UpdateChatDataInput) -> UpdateChatDataOutput:
        
        # Update an existing chat session in Redis by appending a new message.
        
        key = str(chat_data.session_id)
        logger.info(f"Updating chat session {key} in Redis")

        try:
            existing_data = await redis_client.get(key)
            if not existing_data:
                logger.warning(f"Session {key} not found for update")
                raise HTTPException(status_code=404, detail=f"Session {key} does not exist")

            chat_history = json.loads(existing_data)

            # TODO: Add TTL to refresh session expiration if needed

            result: bool = await redis_client.set(key, json.dumps(chat_history))
            if not result:
                logger.error(f"Failed to update chat session {key}")
                raise HTTPException(status_code=500, detail=f"Failed to update session {key}")

            logger.info(f"Session {key} updated successfully")
            return UpdateChatDataOutput(update_status=result, session_id=key)

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while updating chat")
        except Exception as e:
            RedisAPIException.handle_unexpected_error(e, "Unexpected error while updating chat")
