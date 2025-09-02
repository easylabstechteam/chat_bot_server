# ------------------- IMPORTS -------------------
from pydantic import (
    BaseModel,
    Field,
)  # BaseModel for validation; Field for metadata/constraints
from typing import (
    List,
    Optional,
)  # Type hints: List = multiple items, Optional = can be None
from datetime import datetime  # For timestamps
from uuid import UUID  # For unique session identifiers


# ------------------- MESSAGE MODEL -------------------
class Message(BaseModel):

    # Represents a single message in a chat conversation.

    # Attributes:
    #     role (str): Who sent the message ("user" or "assistant").
    #     message (str): The text content of the message.
    #     intent (Optional[str]): Optional detected intent for the message.
    #     timestamp (datetime): When the message was sent.

    role: str = Field(
        ..., description="Role of the sender, e.g., 'user' or 'assistant'"
    )
    message: str = Field(..., description="The text content of the message")
    intent: Optional[str] = Field(
        None, description="Optional intent detected from the message"
    )
    timestamp: datetime = Field(..., description="When the message was sent")


# ------------------- USER MESSAGE INPUT MODEL -------------------
class UserMessage(BaseModel):

    # Represents a new message from the user when continuing a chat session.

    # Attributes:
    #     session_id (UUID): Unique identifier for the chat session.
    #     messages (Message): The message being added to the conversation.

    session_id: UUID = Field(..., description="Unique identifier for the chat session")
    messages: Message = Field(
        ..., description="The new message being added to the chat"
    )


# ------------------- QUESTIONS MODEL -------------------
class Questions(BaseModel):

    # Represents a set of questions that the chatbot might ask.

    # Attributes:
    #     questions (List[str]): List of questions as plain text strings.

    questions: List[str] = Field(
        ..., description="List of questions for the chatbot to ask"
    )


# ------------------- CHAT HISTORY MODEL -------------------
class ChatHistory(BaseModel):

    # Represents the full chat conversation history.

    # Attributes:
    #     messages (List[Message]): All messages exchanged between the user and assistant.

    messages: List[Message] = Field(
        ..., description="List of all messages in the conversation"
    )
