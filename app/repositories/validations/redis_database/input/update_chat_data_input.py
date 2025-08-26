# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field  # BaseModel for validation, Field for metadata/constraints
from uuid import UUID                   # UUID type for strongly-typed session identifiers
from datetime import datetime           # For timestamp fields
from typing import Optional             # For optional fields
import json                             # To convert models to JSON strings

# ------------------- UPDATE CHAT DATA INPUT -------------------
class UpdateChatDataInput(BaseModel):
    # Model for updating chat session data in Redis
    # Contains session information, message content, role, intent, and timestamp

    session_id: Optional[UUID] = Field(
        ...,  # Required field; Optional type allows flexibility in usage
        description="The unique identifier of the chat session"
    )

    role: str = Field(
        ..., 
        min_length=1, max_length=1000, 
        description="The role of the message sender, e.g., 'user' or 'assistant'"
    )

    message: str = Field(
        ..., 
        min_length=1, max_length=1000, 
        description="The content of the chat message"
    )

    intent: str = Field(
        ..., 
        min_length=1, max_length=1000, 
        description="The intent associated with this message, if any"
    )

    timestamp: datetime = Field(
        ..., 
        description="The UTC timestamp when this message was created or updated"
    )

    # ------------------- METHOD: to_json -------------------
    def to_json(self) -> str:
        # Convert UUID and datetime to strings for JSON serialization
        self.session_id = str(self.session_id)
        self.timestamp = str(self.timestamp)

        # Return the model as a JSON-formatted string
        return json.dumps(self.dict())
