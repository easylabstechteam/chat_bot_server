# ------------------- IMPORTS -------------------
# Import the repository to handle interactions with Google Gemini AI (intent detection, chatbot responses)
from repositories.google_genai_llm.google_genai_llm import GoogleGeminaiRepository

# Import the repository to handle Redis database operations (saving and fetching chat data)
from repositories.redis_database.redis_repository import RedisRepository

# Pydantic is used to define data models and validate data
from pydantic import BaseModel, Field

# Import datetime for timestamp fields
from datetime import datetime

# UUID is used to create unique identifiers for chat sessions
from uuid import UUID

# FastAPI HTTPException is used to raise HTTP errors with a status code and message
from fastapi import HTTPException

# Optional allows defining fields that can be None
from typing import Optional


class Message(BaseModel):

    session_id: UUID = Field(None, description="Unique identifier for the chat session")
    # Role of the message sender (e.g., "user" or "assistant")
    role: str = Field(
        ..., description="Role of the sender, e.g., 'user' or 'assistant'"
    )

    # The actual text content of the message
    message: str = Field(..., description="Text content of the message")

    # Optional detected intent of the message
    intent: Optional[str] = Field(None, description="Optional intent of the message")

    # Timestamp when the message was sent
    timestamp: datetime = Field(..., description="Timestamp of the message")


async def converse_and_respond(user_message: Message):
    try:
        # Predefined questions that the chatbot might ask for appointment booking 
        questions = [
            "What date would you like to book the appointment for?",
            "Do you have a preferred time for the appointment?",
            "Which service or type of appointment would you like to book?",
            "Would you like to choose a specific staff member or provider?",
            "Do you have any special requirements or notes for the booking?",
        ]

        # Initialize chat_history variable, will store all messages in the session 
        chat_history: any = None

        # ------------------- DETECT USER INTENT -------------------
        # Use Google Gemini AI to detect what the user's message means
        new_intent = await GoogleGeminaiRepository.intent_detector(
            user_message=user_message
        )

        # If the detected intent is different from the one in the message, update it
        if user_message.intent != new_intent:
            user_message.intent = new_intent

        # ------------------- SAVE MESSAGE TO REDIS -------------------
        if user_message.session_id:
            # If the session already exists, update it with the new message
            await RedisRepository.update_chat_data(user_message)
            # Fetch the full chat history after update
            chat_history = await RedisRepository.get_chat_data(user_message.session_id)

        else:
            # If no session exists, create a new session in Redis
            create_chat_status = await RedisRepository.create_chat_data(user_message)
            # Fetch the chat history for the new session
            chat_history = await RedisRepository.get_chat_data(
                create_chat_status.session_id
            )

        # ------------------- SEND MESSAGE TO LLM -------------------
        # Pass the chat history and predefined questions to the AI to generate a response
        llm_response = await GoogleGeminaiRepository.chatbot_continue_conversation(
            chat_history=chat_history, questions=questions
        )

        # ------------------- SAVE LLM RESPONSE TO REDIS ------------------- 
        save_status = await RedisRepository.update_chat_data(llm_response)

        # ------------------- RETURN RESPONSE -------------------
        # Send the AI's response back to the front-end
        return llm_response

    except Exception as e:
        # If any error occurs, raise an HTTP 500 error with the message
        raise HTTPException(
            status_code=500,
            detail=f"some shit popped up brah, check the situation {str(e)}",
        )
