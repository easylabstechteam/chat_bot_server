# ------------------- IMPORTS -------------------
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ValidationError
from uuid import UUID
from datetime import datetime
import json


# ------------------- CREATE CHAT MESSAGE MODEL -------------------
class CreateChatMessage(BaseModel):

    # Represents a single message in a chat session.
    # Includes the session it belongs to, who sent it, the message content, and timestamp.

    session_id: Optional[UUID] = Field(
        ...,
        description="Unique identifier for the chat session this message belongs to.",
    )

    role: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Role of the sender, e.g., 'user' or 'assistant'.",
    )

    timestamp: str = Field(
        ..., description="Time when this message was sent (ISO format string)."
    )

    message: str = Field(
        ..., min_length=1, max_length=1000, description="The actual message text."
    )

    class Config:
        extra = "allow"  # Allow extra fields (flexibility)

    def to_json(self) -> str:

        # Converts this message into a JSON string.
        # UUIDs and timestamps are converted to strings for storage or API use.

        self.session_id = str(self.session_id)
        self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "CreateChatMessage":

        # Converts a JSON string back into a CreateChatMessage instance.
        # Raises ValueError if JSON is invalid or fields are missing.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Invalid JSON for CreateChatMessage: {e}")


# ------------------- CREATE CHAT DATA INPUT MODEL -------------------
class CreateChatDataInput(BaseModel):

    # Represents data sent when a new chat message is created.
    # This is similar to CreateChatMessage, used for API input validation.

    session_id: Optional[UUID] = Field(
        ..., description="Unique identifier for the chat session."
    )

    role: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Role of the sender (e.g., 'user' or 'assistant').",
    )

    timestamp: str = Field(..., description="Time when the message was sent.")

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The text content of the message.",
    )

    class Config:
        extra = "allow"

    def to_json(self) -> str:

        # Converts this input to JSON string for storage, logging, or sending over API.

        self.session_id = str(self.session_id)
        self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "CreateChatDataInput":

        # Converts JSON string back into a CreateChatDataInput instance.
        # Raises ValueError for invalid JSON or missing fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Invalid JSON for CreateChatDataInput: {e}")


# ------------------- REDIS SET DATA INPUT MODEL -------------------
class RedisSetDataInput(BaseModel):

    # Represents a chat session as stored in Redis.
    # Contains the session ID and all messages in that session.

    session_id: Optional[UUID] = Field(
        ..., description="Unique ID for the chat session."
    )

    messages: List[CreateChatMessage] = Field(
        ..., description="List of all messages in this chat session."
    )

    class Config:
        extra = "allow"

    def to_json(self) -> str:

        # Converts the whole chat session (including all messages) to JSON string.
        # Suitable for storing in Redis.

        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "RedisSetDataInput":

        # Converts JSON string back into RedisSetDataInput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            # Ensure each message is converted into CreateChatMessage instance
            messages_data = data.get("messages", [])
            data["messages"] = [
                CreateChatMessage(**m) if not isinstance(m, CreateChatMessage) else m
                for m in messages_data
            ]
            return cls(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Invalid JSON for RedisSetDataInput: {e}")
