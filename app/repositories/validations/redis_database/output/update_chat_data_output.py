# ------------------- IMPORTS -------------------
import json
from pydantic import BaseModel, Field
from typing import Any, Dict


# ------------------- UPDATE CHAT DATA OUTPUT MODEL -------------------
class UpdateChatDataOutput(BaseModel):

    # Model for returning the result of updating chat data in Redis.
    # Fields:
    # - update_status: True if the update was successful, False otherwise.
    # - session_id: The unique identifier of the chat session that was updated.

    update_status: bool = Field(
        ..., description="Indicates whether the chat update was successful (True/False)"
    )

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The chat session ID for which the update was performed",
    )

    def to_json(self) -> str:

        # Converts this model instance to a JSON string.
        # Useful for returning via API or storing in Redis.

        self.session_id = str(self.session_id)  # Ensure session_id is a string
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "UpdateChatDataOutput":

        # Converts a JSON string back into an UpdateChatDataOutput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for UpdateChatDataOutput: {e}")
