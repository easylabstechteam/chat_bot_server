# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any, Dict
import json


# ------------------- GET CHAT DATA INPUT MODEL -------------------
class GetChatDataInput(BaseModel):

    # Model for validating input when fetching chat data from Redis by session ID.
    # Contains only the session ID.

    session_id: UUID = Field(
        ..., description="The unique UUID of the chat session to fetch from Redis."
    )

    def to_json(self) -> str:

        # Converts this model instance to a JSON string.
        # Useful for storing or transmitting via API.

        self.session_id = str(self.session_id)  # Convert UUID to string for JSON
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) :

        # Converts a JSON string back into a GetChatDataInput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for GetChatDataInput: {e}")
