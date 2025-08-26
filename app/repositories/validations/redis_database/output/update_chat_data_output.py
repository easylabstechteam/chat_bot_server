# ------------------- IMPORTS -------------------
import json
from pydantic import BaseModel, Field  # BaseModel for validation; Field for metadata and constraints

# ------------------- UPDATE CHAT DATA OUTPUT MODEL -------------------
class UpdateChatDataOutput(BaseModel):
    # Model for returning status after updating chat data in Redis

    update_status: bool = Field(
        ...,  # Required field
        description="Indicates whether the chat update was successful (True/False)"
    )
    session_id: str = Field(
        ...,                      # Required field
        min_length=1,             # Minimum string length
        max_length=5000,          # Maximum string length
        description="The chat session ID for which the update was performed"
    )

    # ------------------- METHOD: to_json -------------------
    def to_json(self) -> str:
        # Convert session_id to string for JSON serialization
        self.session_id = str(self.session_id)
        # Return the model as a JSON-formatted string
        return json.dumps(self.dict())
