# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID
import json


# ------------------- CHAT INPUT MODEL -------------------
class ChatInput(BaseModel):

    # Represents a single chat input from a user or assistant.
    # Fields:
    # - session_id: Optional UUID of the chat session.
    # - role: Role of the sender ('user' or 'assistant').
    # - timestamp: Time when the message was sent (ISO string).
    # - message: The text content of the message.

    session_id: Optional[UUID] = Field(..., description="UUID of the chat session")
    role: str = Field(
        ..., min_length=1, max_length=1000, description="Role of the sender"
    )
    timestamp: str = Field(..., description="Timestamp of the message (ISO format)")
    message: str = Field(
        ..., min_length=1, max_length=1000, description="Text content of the message"
    )

    class Config:

        # Allow extra fields for flexibility in future changes.

        extra = "allow"

    def to_json(self) -> str:

        # Converts this chat input instance to a JSON string.

        self.session_id = str(self.session_id) if self.session_id else None
        self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "ChatInput":

        # Converts a JSON string back into a ChatInput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for ChatInput: {e}")
