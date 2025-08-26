import json  # For converting Python objects to JSON string and back
from uuid import UUID, uuid4  # UUID for unique session IDs
from datetime import datetime  # For timestamps

from fastapi import HTTPException  # For raising HTTP errors in FastAPI
from redis.exceptions import RedisError  # To catch Redis-specific errors

from clients.redis_client import redis_client  # Import Redis client instance

# Import Pydantic models for input and output validation
from repositories.validations.redis_database.input.create_chat_data_input import (
    CreateChatDataInput,
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
    GetChatDataOutput,Message
)
from repositories.validations.redis_database.input.update_chat_data_input import (
    UpdateChatDataInput,
)
from repositories.validations.redis_database.output.update_chat_data_output import (
    UpdateChatDataOutput,
)

# Import custom exception handler to standardize Redis/unexpected errors
from repositories.redis_database.errorHandling.redis_api_exceptions import (
    RedisAPIException,
)

# Import universal logger function
from utils.logger_setup import get_logger

# -------------------- Logger --------------------
logger = get_logger(
    "chat_data_logger"
)  # Get a universal logger named 'chat_data_logger'


# -------------------- Redis Repository --------------------
class RedisRepository:

    # Class containing all CRUD operations for chat data stored in Redis.
    # Methods are static because we don't need instance state.

    @staticmethod
    async def create_chat_data(chat_data: CreateChatDataInput) -> CreateChatDataOutput:

        # Create a new chat session in Redis.

        key = str(uuid4())  # Generate a unique session ID as a string
        chat_data.session_id = key  # Assign generated session ID to chat data
        logger.info(f"Creating new chat session with ID: {key}")  # Log session creation

        try:
            # TODO: Add TTL here to expire session automatically, e.g., ex=3600 for 1 hour

            result: bool = await redis_client.set(
                key, chat_data.to_json()
            )  # Save chat data to Redis as JSON string
            if not result:  # If Redis failed to save
                logger.error(f"Failed to save chat data for session {key}")  # Log error
                raise HTTPException(
                    status_code=500, detail="Failed to save chat data"
                )  # Raise HTTP 500

            logger.info(
                f"Chat data saved successfully for session {key}"
            )  # Log success
            return CreateChatDataOutput(
                update_status=result, session_id=key
            )  # Return Pydantic output model

        except RedisError as e:  # Handle Redis-specific exceptions
            RedisAPIException.handle_redis_error(
                e, "Redis error while creating chat"
            )  # Use centralized handler

        except Exception as e:  # Handle unexpected exceptions
            RedisAPIException.handle_unexpected_error(
                e, "Unexpected error while creating chat"
            )  # Centralized handler

    @staticmethod
    async def delete_chat_data(session_id: DeleteChatDataInput) -> DeleteChatDataOutput:

        # Delete an existing chat session from Redis.

        key = str(session_id)  # Convert session ID to string for Redis key
        logger.info(f"Deleting chat session {key} from Redis")  # Log deletion attempt

        try:
            result: int = await redis_client.delete(
                key
            )  # Attempt to delete the session key
            if result == 0:  # If Redis returned 0, key did not exist
                logger.warning(f"Session {key} not found in Redis")  # Log warning
                raise HTTPException(
                    status_code=404, detail=f"Session {key} does not exist"
                )  # Raise 404

            logger.info(f"Session {key} deleted successfully")  # Log success
            return DeleteChatDataOutput(
                delete_status=result, session_id=key
            )  # Return output model

        except RedisError as e:  # Handle Redis-specific errors
            RedisAPIException.handle_redis_error(e, "Redis error while deleting chat")

        except Exception as e:  # Handle unexpected errors
            RedisAPIException.handle_unexpected_error(
                e, "Unexpected error while deleting chat"
            )

    @staticmethod
    async def get_chat_data(session_id: UUID) -> GetChatDataOutput:
        key = str(session_id)
        logger.info(f"Fetching chat session {key} from Redis")

        try:
            response = await redis_client.get(key)
            if not response:
                logger.warning(f"Session {key} not found in Redis")
                raise HTTPException(status_code=404, detail=f"Session {key} not found")

            chat_dict = json.loads(response)

            # ------------------- PREPROCESS MESSAGES -------------------
            messages_data = chat_dict.get("messages", [])
            for msg in messages_data:
                # Ensure 'intent' is always a string
                intent_value = msg.get("intent")
                if isinstance(intent_value, dict):
                    msg["intent"] = intent_value.get("detected_intent", "unknown")
                elif intent_value is None:
                    msg["intent"] = "unknown"

                # Convert timestamp string to datetime object if needed
                if isinstance(msg.get("timestamp"), str):
                    try:
                        msg["timestamp"] = datetime.fromisoformat(msg["timestamp"])
                    except ValueError:
                        # Fallback if timestamp is not ISO formatted
                        msg["timestamp"] = datetime.strptime(msg["timestamp"], "%Y-%m-%d %H:%M:%S%z")

            # Create Pydantic Message objects
            messages = [Message(**msg) for msg in messages_data]

            return GetChatDataOutput(
                session_id=session_id,
                form=chat_dict.get("form"),
                intent=chat_dict.get("intent", "unknown"),
                messages=messages
            )

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while fetching chat")

        except Exception as e:
            RedisAPIException.handle_unexpected_error(e, "Unexpected error while fetching chat")
    @staticmethod
    async def update_chat_data(chat_data: UpdateChatDataInput) -> UpdateChatDataOutput:

        # Update an existing chat session in Redis by appending a new message.

        key = str(chat_data.session_id)  # Convert session ID to string
        logger.info(f"Updating chat session {key} in Redis")  # Log update attempt

        try:
            existing_data = await redis_client.get(key)  # Fetch existing session
            if not existing_data:  # If session does not exist
                logger.warning(f"Session {key} not found for update")  # Log warning
                raise HTTPException(
                    status_code=404, detail=f"Session {key} does not exist"
                )  # Raise 404

            chat_history = json.loads(
                existing_data
            )  # Convert existing session JSON to dict
            new_message = chat_data.dict()  # Convert new message input to dictionary

            # Ensure UUID and timestamp are strings for JSON serialization
            if isinstance(new_message.get("session_id"), UUID):
                new_message["session_id"] = str(new_message["session_id"])
            if isinstance(new_message.get("timestamp"), datetime):
                new_message["timestamp"] = new_message["timestamp"].isoformat()

            # Append new message to existing messages list
            chat_history.setdefault("messages", []).append(new_message)

            # TODO: Add TTL here too if you want updated session to reset expiration

            result: bool = await redis_client.set(
                key, json.dumps(chat_history)
            )  # Save updated session
            if not result:  # If saving failed
                logger.error(f"Failed to update chat session {key}")  # Log error
                raise HTTPException(
                    status_code=500, detail=f"Failed to update session {key}"
                )  # Raise 500

            logger.info(f"Session {key} updated successfully")  # Log success
            return UpdateChatDataOutput(
                update_status=result, session_id=key
            )  # Return output model

        except RedisError as e:
            RedisAPIException.handle_redis_error(e, "Redis error while updating chat")

        except Exception as e:
            RedisAPIException.handle_unexpected_error(
                e, "Unexpected error while updating chat"
            )
