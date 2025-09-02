# ------------------- IMPORTS -------------------
import json
from pydantic import BaseModel, Field
from typing import Any, Dict


# ------------------- CREATE CHAT DATA OUTPUT MODEL -------------------
class CreateChatDataOutput(BaseModel):

    #     Model for returning the result of creating or updating chat data in Redis.
    #     Fields:
    #     - update_status: indicates whether the operation was successful.
    #     - session_id: the unique identifier of the chat session.

    update_status: bool = Field(
        ..., description="Indicates whether the create/update operation succeeded."
    )

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The unique identifier of the chat session.",
    )

    def to_json(self) -> str:

        # Converts this output model to a JSON string.
        # Useful for returning as API response or logging.

        self.session_id = str(self.session_id)  # Ensure session_id is a string
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str) -> "CreateChatDataOutput":

        # Converts a JSON string back into a CreateChatDataOutput instance.
        # Raises ValueError if JSON is invalid or missing required fields.

        try:
            data: Dict[str, Any] = json.loads(json_str)
            return cls(**data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid JSON for CreateChatDataOutput: {e}")
