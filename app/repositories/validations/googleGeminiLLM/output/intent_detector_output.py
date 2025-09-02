# ------------------- IMPORTS -------------------
from typing import List, Any, Dict
from pydantic import BaseModel, Field, ValidationError
from uuid import UUID
from datetime import datetime
import json


# ------------------- INTENT DETECTOR OUTPUT MODEL -------------------
class IntentDetectorOutput(BaseModel):

    # This model represents what we send back after detecting a user's intent.
    # It includes:
    # - The session ID for this chat
    # - The detected intent (what the user wants)
    # - Follow-up questions based on that intent

    # Unique ID for the chat session (to know which chat this belongs to)
    session_id: UUID = Field(..., description="Unique identifier for the chat session.")

    # What we think the user wants (e.g., 'book_appointment', 'ask_pricing')
    detected_intent: str = Field(
        ...,
        min_length=1,  # Must not be empty
        max_length=255,  # Shouldn't be too long
        description="The detected intent from the user's message.",
    )

    # Questions we might ask the user next to get more details
    questions: List[str] = Field(
        ..., description="List of follow-up questions based on the detected intent."
    )

    class Config:

        # Extra settings for this model:
        # - Do not allow unknown fields
        # - Automatically validate fields when we assign new values
        # - Convert UUIDs and datetimes into strings when making JSON

        extra = "forbid"
        validate_assignment = True
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}

    def to_json(self) -> str:

        # Turn this model into a JSON string.
        # Useful for saving into Redis or sending over an API.

        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "IntentDetectorOutput":

        # Take a JSON string and turn it back into a model.
        # If the data is wrong or broken, it will raise an error.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Invalid JSON for IntentDetectorOutput: {e}")
