# ------------------- IMPORTS -------------------
import json
from pydantic import BaseModel, Field
from typing import Any, Dict


# ------------------- DELETE CHAT DATA OUTPUT MODEL -------------------
class DeleteChatDataOutput(BaseModel):

    # Model for returning the result of deleting chat data from Redis.
    # Fields:
    # - delete_status: status code indicating if the delete operation succeeded.
    # - session_id: the unique identifier of the chat session that was deleted.

    delete_status: int = Field(
        ..., description="Status code indicating the result of the delete operation."
    )

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The unique identifier of the chat session that was deleted.",
    )

    def to_json(self) -> str:

        # Converts this output model to a JSON string.
        # Useful for returning as an API response or for logging.

        self.session_id = str(self.session_id)  # Ensure session_id is a string
        self.delete_status = int(self.delete_status)  # Ensure delete_status is int
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "DeleteChatDataOutput":
        
        # Converts a JSON string back into a DeleteChatDataOutput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for DeleteChatDataOutput: {e}")
