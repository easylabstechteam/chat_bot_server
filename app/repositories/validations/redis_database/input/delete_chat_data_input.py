# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any, Dict
import json


# ------------------- DELETE CHAT DATA INPUT MODEL -------------------
class DeleteChatDataInput(BaseModel):

    # Model for validating input when deleting chat data from Redis.
    # Contains only the session ID of the chat data to delete.

    session_id: UUID = Field(
        ..., description="The unique UUID of the chat data to be deleted from Redis."
    )

    def to_json(self) -> str:

        # Converts this model instance to a JSON string.
        # Useful for storing, logging, or sending via an API.

        self.session_id = str(self.session_id)  # Convert UUID to string for JSON
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "DeleteChatDataInput":

        # Converts a JSON string back into a DeleteChatDataInput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for DeleteChatDataInput: {e}")
