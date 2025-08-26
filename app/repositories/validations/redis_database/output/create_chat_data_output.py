# ------------------- IMPORTS -------------------
import json
from pydantic import BaseModel, Field  # BaseModel for validation, Field for metadata/constraints

# ------------------- CREATE CHAT DATA OUTPUT -------------------
class CreateChatDataOutput(BaseModel):
    # Model for returning the result of creating/updating chat data in Redis
    # Contains:
    # - update_status: whether the operation was successful
    # - session_id: the identifier of the chat session

    update_status: bool = Field(
        ...,  # Required field
        description="Indicates whether the create/update operation succeeded"
    )

    session_id: str = Field(
        ..., 
        min_length=1, max_length=5000, 
        description="The unique identifier of the chat session"
    )

    # ------------------- METHOD: to_json -------------------
    def to_json(self) -> str:
        # Convert the session_id to string (if not already) for JSON serialization
        self.session_id = str(self.session_id)

        # Return the model as a JSON-formatted string
        return json.dumps(self.dict())
