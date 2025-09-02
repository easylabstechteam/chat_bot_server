# ------------------- IMPORTS -------------------
from typing import Optional, List  # Optional = field can be None, List = list of items
from pydantic import BaseModel, Field  # Used to define and validate data models
from uuid import UUID  # For unique session IDs
import json  # For converting Python objects to JSON strings
from datetime import datetime  # To work with date & time


# ------------------- INTENT DETECTOR INPUT MODEL -------------------
class IntentDetectorInput(BaseModel):

    # Represents the input data for the intent detection system.
    # This model includes session information, the message details,
    # and who sent it

    # Unique identifier for the chat session (optional, may be None)
    session_id: Optional[UUID] = Field(
        ...,  # Required (but can be None if not provided)
        description="Unique ID of the chat session (can be None)",
    )

    # Who sent the message (e.g., 'user' or 'assistant')
    role: str = Field(
        ...,  # Required
        min_length=1,  # Must be at least 1 character
        max_length=1000,  # Cannot exceed 1000 characters
        description="The role of the sender, e.g., 'user' or 'assistant'",
    )

    # When the message was sent (stored as a string, e.g., '2025-09-02T14:30:00')
    timestamp: str = Field(
        ...,  # Required
        description="Timestamp of when the message was sent (as string)",
    )

    # The actual message text
    message: str = Field(
        ...,  # Required
        min_length=1,  # Minimum length 1 character
        max_length=1000,  # Maximum length 1000 characters
        description="The message content sent by the user or assistant",
    )

    class Config:
        # Allow extra fields not defined in the model (flexible schema)
        extra = "allow"

    def to_json(self) -> str:

        # Converts the model into a JSON string.
        # Ensures UUID and timestamp are converted to strings (JSON can't handle UUIDs directly).

        # Convert session_id to string (if it's a UUID)
        self.session_id = str(self.session_id)

        # Ensure timestamp is a string
        self.timestamp = str(self.timestamp)

        # Convert the model into a JSON-formatted string
        return json.dumps(self.dict())
