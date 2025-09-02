# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID
import json


# ------------------- MESSAGE MODEL -------------------
class Message(BaseModel):

    # Represents a single message in a chat session.
    # Fields:
    # - session_id: Optional UUID of the chat session this message belongs to.
    # - role: Role of the sender ('user' or 'assistant').
    # - timestamp: Time when the message was sent (ISO string).
    # - message: The actual text content of the message.

    session_id: Optional[UUID] = Field(..., description="UUID of the chat session")
    role: str = Field(
        ..., min_length=1, max_length=1000, description="Role of the sender"
    )
    timestamp: str = Field(..., description="Timestamp of the message (ISO format)")
    message: str = Field(
        ..., min_length=1, max_length=1000, description="Message content"
    )

    class Config:

        # Allow extra fields for flexibility in future changes.

        extra = "allow"

    def to_json(self) -> str:

        # Converts this message instance to a JSON string.

        self.session_id = str(self.session_id) if self.session_id else None
        self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "Message":

        # Converts a JSON string back into a Message instance.
        # Raises ValueError if JSON is invalid.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for Message: {e}")


# ------------------- GET CHAT DATA OUTPUT MODEL -------------------
class GetChatDataOutput(BaseModel):

    # Represents the output when fetching chat data from Redis.
    # Fields:
    # - session_id: UUID of the chat session.
    # - messages: List of messages in the chat session.

    session_id: UUID = Field(
        ..., description="Session identifier for this chat session"
    )
    messages: List[Message] = Field(
        default_factory=list, description="List of chat messages in the session"
    )

    def to_json(self) -> str:

        # Converts this output model to a JSON string.

        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "GetChatDataOutput":

        # Converts a JSON string back into a GetChatDataOutput instance.
        # Raises ValueError if JSON is invalid.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for GetChatDataOutput: {e}")
