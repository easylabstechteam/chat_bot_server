# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# ------------------- MESSAGE MODEL -------------------
class Message(BaseModel):
    # Role of the message sender (e.g., "user" or "assistant")
    role: str = Field(..., description="Role of the sender, e.g., 'user' or 'assistant'")

    # The actual text content of the message
    message: str = Field(..., description="Text content of the message")

    # Optional detected intent of the message
    intent: Optional[str] = Field(None, description="Optional intent of the message")

    # Timestamp when the message was sent
    timestamp: datetime = Field(..., description="Timestamp of the message")

# ------------------- CHATBOT CONTINUE CONVERSATION INPUT -------------------
class ChatBotContinueConversationInput(BaseModel):
    # Unique ID for the chat session
    session_id: UUID = Field(..., description="Unique identifier for the chat session")

    # Optional form data if provided by the user
    form: Optional[dict] = Field(None, description="Optional form data submitted by the user")

    # Optional current intent of the conversation
    intent: Optional[str] = Field(None, description="Optional current intent of the conversation")

    # List of past messages in the conversation
    messages: List[Message] = Field(..., description="List of messages in the chat history")

# ------------------- QUESTIONS MODEL -------------------
class Questions(BaseModel):
    # List of questions to ask the user
    questions: List[str] = Field(..., description="List of questions for the chatbot to ask")

    