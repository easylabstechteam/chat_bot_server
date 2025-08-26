# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from uuid import UUID
import json

# ------------------- DELETE CHAT DATA INPUT -------------------
class DeleteChatDataInput(BaseModel):
    # Required UUID of the chat session or data to delete from Redis
    session_id: UUID = Field(
        ...,  # Ellipsis indicates that this field is required
        description="The unique UUID of the chat data to be deleted from Redis"
    )

    # Convert the model to a JSON string for storage or transmission
    def to_json(self) -> str:
        # Convert UUID to string so it can be serialized to JSON
        self.session_id = str(self.session_id)
        # DeleteChatDataInput does not have a timestamp, so this line should be removed
        # self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())  # Convert the model dictionary to JSON
