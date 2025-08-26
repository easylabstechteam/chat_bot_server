# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field  # BaseModel for validation, Field for metadata
from uuid import UUID                   # UUID type for strongly-typed session identifiers
import json                             # For converting models to JSON strings

# ------------------- GET CHAT DATA INPUT -------------------
class GetChatDataInput(BaseModel):
    # Model for validating input when fetching chat data from Redis by session ID
    
    session_id: UUID = Field(
        ...,           # Ellipsis indicates that this field is required
        description="The unique UUID of the chat session to fetch from Redis"
        # min_length and max_length are unnecessary for UUID; removed for clarity
    )

    # Convert the model instance to a JSON string for storage or transmission
    def to_json(self) -> str:
        # Convert UUID to string for JSON serialization
        self.session_id = str(self.session_id)
        # Remove self.timestamp as this model does not have a timestamp
        # self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())  # Serialize the model's dictionary to JSON
