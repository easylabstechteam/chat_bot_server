# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import json

# ------------------- CREATE CHAT DATA INPUT -------------------
class CreateChatDataInput(BaseModel):
    # Optional UUID for the session; if not provided, a new session can be created
    session_id: Optional[UUID] = Field(..., description="Unique identifier for the chat session")
    
    # Role of the message sender (e.g., 'user' or 'assistant')
    role: str = Field(..., description="Role of the message sender")
    
    # The actual message content
    message: str = Field(..., description="The text content of the chat message")
    
    # Intent associated with the message
    intent: str = Field(..., description="The detected or assigned intent of the message")
    
    # Timestamp when the message was created
    timestamp: datetime = Field(..., description="The timestamp of the message")

    # Convert the model to a JSON string for storing in Redis
    def to_json(self) -> str:
        self.session_id = str(self.session_id)  # Convert UUID to string
        self.timestamp = str(self.timestamp)    # Convert datetime to string
        return json.dumps(self.dict())          # Convert the dictionary to JSON


# ------------------- MESSAGE MODEL -------------------
class Message(BaseModel):
    # Optional session ID
    session_id: Optional[UUID] = Field(None, description="Unique identifier for the chat session")
    
    # Role of the sender
    role: str = Field(None, description="Role of the message sender")
    
    # Text content of the message
    message: str = Field(None, description="The text content of the message")
    
    # Intent associated with the message
    intent: str = Field(None, description="Intent of the message")
    
    # Timestamp of the message
    timestamp: datetime = Field(None, description="The timestamp of the message")

    # Convert the message to a JSON string for storage
    def to_json(self) -> str:
        self.session_id = str(self.session_id)
        self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())


# ------------------- REDIS SET DATA INPUT -------------------
class RedisSetDataInput(BaseModel):
    # Optional session ID
    session_id: Optional[UUID] = Field(None, description="Unique identifier for the chat session")
    
    # Form data associated with the chat session (optional)
    form: str = Field(None, description="Optional form data for the session")
    
    # Intent of the session (optional)
    intent: str = Field(None, description="Current intent of the session")
    
    # List of messages in the session
    messages: List[Message] = Field(None, description="List of messages in the chat session")

    # Convert the model to a JSON string for storage
    def to_json(self) -> str:
        self.session_id = str(self.session_id)
        # Note: RedisSetDataInput does not have a timestamp directly; this line might need adjustment
        # self.timestamp = str(self.timestamp)  # Only if timestamp exists
        return json.dumps(self.dict())


# input f