# ------------------- IMPORTS -------------------
import json  # Used to convert Python objects to JSON (and back)
from uuid import UUID, uuid4  # For creating unique session IDs
from datetime import datetime  # To get the current date and time

# FastAPI tools for error handling
from fastapi import HTTPException  # To send standard HTTP errors (e.g., 404, 500)
from redis.exceptions import RedisError  # To handle Redis-specific errors

# Redis client that communicates with the Redis database
from clients.redis_client import redis_client

# Pydantic models (used to validate and structure data)
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

# Custom error handler to standardize Redis-related errors
from repositories.redis_database.errorHandling.redis_api_exceptions import (
    RedisAPIException,
)

# Logger to track what's happening (for debugging and monitoring)
from utils.logger_setup import get_logger

# ------------------- LOGGER -------------------
# Create a logger specifically for this module, named "chat_data_logger"
logger = get_logger("chat_data_logger")


# ------------------- REDIS REPOSITORY -------------------
class RedisRepository:

    # This class handles all chat-related interactions with the Redis database.

    # It provides CRUD operations:
    # - Create: Start a new chat session
    # - Read: Retrieve an existing session's messages
    # - Update: Add new messages to an existing session
    # - Delete: Remove a session

    # ------------------- CREATE CHAT DATA -------------------
    @staticmethod
    async def create_chat_data(
        user_message: CreateChatDataInput,
    ) -> CreateChatDataOutput:

        # Creates a new chat session in Redis.
        # Stores the first user message in the session.

        # Generate a unique session ID for this chat
        key = str(uuid4())
        user_message.session_id = key  # Attach this ID to the incoming message
        logger.info(f"Creating new chat session with ID: {key}")

        try:
            # Create a message object (this is what will be saved in Redis)
            message_obj = CreateChatMessage(
                session_id=user_message.session_id,
                role="user",  # The message is coming from the user
                timestamp=str(datetime.utcnow()),  # Current UTC time
                message=user_message.message,  # The text message itself
            )

            # Convert the message into a Redis-compatible JSON payload
            redis_payload = RedisSetDataInput(
                session_id=user_message.session_id,
                messages=[message_obj],  # Start with one message in the list
            ).to_json()

            # Save the chat data to Redis (key-value pair: session_id -> messages)
            result: bool = await redis_client.set(key, redis_payload)

            # If saving failed, raise an error
            if not result:
                logger.error(f"Failed to save chat data for session {key}")
                raise HTTPException(status_code=500, detail="Failed to save chat data")

            logger.info(f"Chat data saved successfully for session {key}")
            return CreateChatDataOutput(update_status=result, session_id=key)

        except RedisError as e:
            # If something goes wrong with Redis, handle it
            RedisAPIException.handle_redis_error(e, "Redis error while creating chat")
        except Exception as e:
            # Catch any unexpected errors
            RedisAPIException.handle_unexpected_error(
                e, "Unexpected error while creating chat"
            )

    # ------------------- DELETE CHAT DATA -------------------
    @staticmethod
    async def delete_chat_data(session_id: DeleteChatDataInput) -> DeleteChatDataOutput:

        # Deletes an existing chat session from Redis using its session ID.

        key = str(session_id)
        logger.info(f"Deleting chat session {key} from Redis")

        try:
            # Delete the session from Redis
            result: int = await redis_client.delete(key)

            # If result is 0, the session does not exist
            if result == 0:
                logger.warning(f"Session {key} not found in Redis")
                raise HTTPException(
                    status_code=404, detail=f"Session {key} does not exist"
                )

            logger.info(f"Session {key} deleted successfully")
            return DeleteChatDataOutput(delete_status=result, session_id=key)

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while deleting chat")
        except Exception as e:
            RedisAPIException.handle_unexpected_error(
                e, "Unexpected error while deleting chat"
            )

    # ------------------- GET CHAT DATA -------------------
    @staticmethod
    async def get_chat_data(session_id: UUID) -> GetChatDataOutput:

        # Fetches all messages from a chat session stored in Redis.

        key = str(session_id)
        logger.info(f"Fetching chat session {key} from Redis")

        try:
            # Retrieve the chat data from Redis
            response = await redis_client.get(key)

            # If nothing is found, return a 404 error
            if not response:
                logger.warning(f"Session {key} not found in Redis")
                raise HTTPException(status_code=404, detail=f"Session {key} not found")

            # Convert the stored JSON back to a Python dictionary
            chat_dict = json.loads(response)

            # Return the chat messages
            return GetChatDataOutput(
                session_id=session_id, messages=chat_dict.get("messages")
            )

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while fetching chat")
        except Exception as e:
            RedisAPIException.handle_unexpected_error(
                e, "Unexpected error while fetching chat"
            )

    # ------------------- UPDATE CHAT DATA -------------------
    @staticmethod
    async def update_chat_data(chat_data: UpdateChatDataInput) -> UpdateChatDataOutput:

        # Updates an existing chat session in Redis by adding a new message.

        key = str(chat_data.session_id)
        logger.info(f"Updating chat session {key} in Redis")

        try:
            # Fetch the existing chat data
            existing_data = await redis_client.get(key)

            # If session does not exist, return a 404 error
            if not existing_data:
                logger.warning(f"Session {key} not found for update")
                raise HTTPException(
                    status_code=404, detail=f"Session {key} does not exist"
                )

            # Convert the existing JSON data into Python dictionary
            chat_history = json.loads(existing_data)

            # TODO: Add a new message to chat_history["messages"] here if needed
            # TODO: Optionally, refresh the session expiration (TTL)

            # Save the updated chat history back into Redis
            result: bool = await redis_client.set(key, json.dumps(chat_history))

            # If update fails, raise an error
            if not result:
                logger.error(f"Failed to update chat session {key}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to update session {key}"
                )

            logger.info(f"Session {key} updated successfully")
            return UpdateChatDataOutput(update_status=result, session_id=key)

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while updating chat")
        except Exception as e:
            RedisAPIException.handle_unexpected_error(
                e, "Unexpected error while updating chat"
            )
