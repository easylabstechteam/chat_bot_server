# ------------------- IMPORTS -------------------
import json
from pydantic import BaseModel, Field  # BaseModel for validation, Field for metadata/constraints

# ------------------- DELETE CHAT DATA OUTPUT -------------------
class DeleteChatDataOutput(BaseModel):
    # Model for returning the result of deleting chat data from Redis
    # Contains:
    # - delete_status: status code indicating if the delete operation succeeded
    # - session_id: the identifier of the chat session that was deleted

    delete_status: int = Field(
        ...,  # Required field
        description="Status code indicating the result of the delete operation"
    )

    session_id: str = Field(
        ..., 
        min_length=1, max_length=5000, 
        description="The unique identifier of the chat session that was deleted"
    )

    # ------------------- METHOD: to_json -------------------
    def to_json(self) -> str:
        # Convert fields to string for JSON serialization
        self.session_id = str(self.session_id)
        self.delete_status = str(self.delete_status)

        # Return the model as a JSON-formatted string
        return json.dumps(self.dict())
