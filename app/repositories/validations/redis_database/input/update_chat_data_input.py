# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Dict
import json


# ------------------- UPDATE CHAT DATA INPUT MODEL -------------------
class UpdateChatDataInput(BaseModel):

    # Represents a new message being added to an existing chat session.
    # Includes:
    # - session_id: which chat session this message belongs to
    # - role: who sent the message ('user' or 'assistant')
    # - timestamp: when the message was sent
    # - message: the message content

    session_id: Optional[UUID] = Field(
        ..., description="Unique identifier for the chat session being updated."
    )

    role: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Role of the sender, e.g., 'user' or 'assistant'.",
    )

    timestamp: str = Field(
        ..., description="Time when the message was sent (ISO format string)."
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The content of the new message being added to the chat.",
    )

    class Config:

        # Extra settings for production readiness:
        # - Allow extra fields (flexible for future changes)

        extra = "allow"

    def to_json(self) -> str:

        # Converts this input model to a JSON string for storing in Redis or sending over an API.

        self.session_id = str(self.session_id)
        self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "UpdateChatDataInput":

        # Converts a JSON string back into an UpdateChatDataInput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for UpdateChatDataInput: {e}")
