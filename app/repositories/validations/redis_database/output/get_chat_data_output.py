# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import json

# ------------------- MESSAGE MODEL -------------------
class Message(BaseModel):
    role: str = Field(
        default="user",
        min_length=1,
        max_length=1000,
        description="Role of the message sender, e.g., 'user' or 'assistant'"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Content of the chat message"
    )
    intent: str = Field(
        default="unknown",
        min_length=1,
        max_length=1000,
        description="Intent associated with the message"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the message, preferably timezone-aware"
    )

    def to_json(self) -> str:
        return json.dumps(self.dict())

# ------------------- GET CHAT DATA OUTPUT MODEL -------------------
class GetChatDataOutput(BaseModel):
    session_id: UUID = Field(..., description="Session identifier for this chat session")
    form: Optional[str] = Field(default=None, description="Form name or type if applicable")
    intent: str = Field(default="unknown", description="Overall session intent")
    messages: List[Message] = Field(default_factory=list, description="List of chat messages in the session")

    def to_json(self) -> str:
        return json.dumps(self.dict())