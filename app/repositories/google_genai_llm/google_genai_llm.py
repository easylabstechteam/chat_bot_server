# TODO: Replace get_intentions_list() static return with a real database query
# TODO: Add caching for the intents list to reduce DB calls on high traffic
# TODO: Ensure proper error handling if the database is unreachable

# TODO: Wrap all LLM calls (llm.agenerate) with retry logic and exponential backoff
# TODO: Add timeout handling for LLM responses
# TODO: Validate the LLM output format and add fallback handling
# TODO: Log LLM failures and unusual outputs for monitoring

# TODO: Limit the length of user_message to prevent abuse or excessive token usage
# TODO: Sanitize user inputs to avoid injection attacks or unsafe prompts
# TODO: Validate chat_history and questions objects before sending to LLM
# TODO: Mask sensitive data in logs to avoid exposing user information

# TODO: Track and log unknown or unexpected intents returned by the LLM
# TODO: Implement fallback actions for unknown intents
# TODO: Normalize intent strings consistently before further processing

# TODO: Ensure session_id is always validated and consistent
# TODO: Track conversation context persistently (DB or cache)
# TODO: Implement multi-turn conversation handling
# TODO: Validate questions object: ensure correct ordering and non-empty

# TODO: Add caching for repeated prompts or common user messages
# TODO: Consider batching LLM requests for multiple messages
# TODO: Implement rate-limiting for LLM calls
# TODO: Profile response times and optimize prompt length

# TODO: Centralize logs for intent classification errors and chat failures
# TODO: Log LLM response time for performance monitoring
# TODO: Alert on repeated LLM failures or invalid outputs

# TODO: Write unit tests for intent detection logic
# TODO: Write unit tests for chatbot continuation formatting
# TODO: Write unit tests for error handling
# TODO: Write integration tests for LLM calls (mocked or sandbox)
# TODO: Write integration tests for database interactions
# TODO: Write end-to-end tests to simulate user conversations

# TODO: Add fallback LLM prompt if the model fails to classify intent
# TODO: Add analytics metrics for intents, response times, etc.
# TODO: Consider multi-language support in the future
# TODO: Implement asynchronous task queue (Celery, RQ) for high-load LLM processing

# ------------------- IMPORTS -------------------

# Import FastAPI's HTTPException to handle errors and send HTTP responses
from fastapi import HTTPException

# Import LangChain's PromptTemplate (for building prompts)
# and message types (System, Human, AI) for chat-based LLM interactions
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from uuid import UUID

# Import typing helpers to specify list types and union types
from typing import List, Union

# Import datetime for adding timestamps to chatbot responses
from datetime import datetime

# Import your custom LLM client that supports asynchronous calls
from clients.langchain_client import llm

# Import a logger setup function to log events, warnings, and errors
from utils.logger_setup import get_logger

# Import Pydantic input models for validating user input in chat
from repositories.validations.googleGeminiLLM.input.chat_bot_continue_input import (
ChatHistory, Questions
)

# Import output models for validating responses from the chatbot
from repositories.validations.googleGeminiLLM.output.chat_bot_continue_output import (
    ChatBotContinueOutput,
)

# Import Pydantic input/output models for intent detection
from repositories.validations.googleGeminiLLM.input.intent_detector_input import (
    IntentDetectorInput,
)
from repositories.validations.googleGeminiLLM.output.intent_detector_output import (
    IntentDetectorOutput,
)

# ------------------- LOGGER -------------------

# Create a logger instance to log information, warnings, and errors
logger = get_logger()

# ------------------- HELPER FUNCTION -------------------


# A simple function to return a list of known intents
# In production, this could fetch intents from a PostgreSQL database
async def get_intentions_list() -> List[str]:
    return ["appointment", "unknown"]


# ------------------- LLM REPOSITORY -------------------


class GoogleGeminaiRepository:

    # Repository class for interacting with a LangChain LLM in a chatbot context.
    # Handles:
    # - Detecting user intent
    # - Continuing conversations using chat history and questions

    # -------- INTENT DETECTION METHOD --------
    @staticmethod
    async def intent_detector(user_message: IntentDetectorInput):
        try:
            # Grab the list of intents (could be fetched from DB)
            intents = ["booking", "quote", "build lead times", "accounts", "unknown"]

            # Prepare the system prompt
            prompt = f"""You are an intent detector. Your task is to classify the following message into one of the possible intents:
{intents}

Please respond with the one that is closely matched to the list above. If nothing seems to match, then respond with "unknown".
"""
            system_prompt = prompt  # If using PromptTemplate, integrate here

            # Prepare messages for LLM
            message = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message.message),
            ]

            # Call LLM
            response = await llm.agenerate(messages=[message])
            detected_intent_text = response.generations[0][0].text.strip().lower()

            # Define questions
            booking_questions = [
                "What type of travel will you be booking (e.g. flight, hotel, rental car)?",
                "Where is your destination and when do you plan to arrive?",
                "How many people will be traveling with you?",
                "Do you have any specific dates or time frames in mind for your trip?",
                "Are there any special requirements or preferences for your booking (e.g. seat selection, room type)?",
            ]
            quote_questions = [
                "What services or products are you interested in getting a quote for?",
                "Can you provide more details about the project or scope of work?",
                "What is your estimated budget for this project?",
                "Are there any specific requirements or deadlines that need to be met?",
                "Have you received quotes from other vendors on similar projects?",
            ]
            build_lead_times_questions = [
                "How many hours do you typically spend on a task like this?",
                "Can you walk me through the steps involved in completing this task?",
                "What tools or resources do you currently use to manage your workflow?",
                "Are there any bottlenecks or roadblocks that slow down your work process?",
                "Have you considered implementing any new processes or systems to improve efficiency?",
            ]
            accounts_questions = [
                "Can you provide more details about the disputed charge on your account?",
                "How did you discover the error in your account?",
                "What steps have you taken so far to resolve this issue?",
                "Are there any supporting documents or receipts that can help us investigate further?",
                "Would you like to proceed with a refund or credit to your account?",
            ]
            unknown_questions = []

            # Switch-style mapping using match/case
            match detected_intent_text:
                case "booking":
                    intent_based_questions = booking_questions
                case "quote":
                    intent_based_questions = quote_questions
                case "build lead times":
                    intent_based_questions = build_lead_times_questions
                case "accounts":
                    intent_based_questions = accounts_questions
                case "unknown":
                    intent_based_questions = unknown_questions
                case _:  # default case
                    intent_based_questions = unknown_questions

            # Return structured output
            return IntentDetectorOutput(
                session_id=user_message.session_id,
                detected_intent=detected_intent_text,
                questions=intent_based_questions,
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Issue(s) encountered when detecting user intent: {str(e)}",
            )
    # -------- CHATBOT CONTINUATION METHOD --------



    @staticmethod
    async def chatbot_continue_conversation(session_id:UUID, 
        chat_history: ChatHistory ,  # Past messages in the chat
        questions: Questions ,  # List of questions or Questions object
    ) -> ChatBotContinueOutput:

        # Continue a chatbot conversation using LangChain LLM.
        # - Uses previous chat history and a list of questions
        # - Generates an AI response based on instructions


        # -------------------- Step 1: Define PromptTemplate --------------------
        # Template instructs the LLM on how to respond
        prompt_template = PromptTemplate(
            input_variables=["questions", "chat_history"],  # Placeholders to fill
            template="""
            You are an intelligent and helpful assistant. Your role is to interact with the user by asking specific questions that are provided from a PostgreSQL database, and by responding accurately and politely to any user questions. You will also be provided with previous chat history, and your responses should continue the conversation seamlessly from where it left off. Follow these rules strictly:

            1. Always ask the questions provided below. Do not change the subject of the question.
            2. Keep the conversation strictly on topic. Do not introduce unrelated topics or personal opinions.
            3. Continue the conversation naturally from the last message without repeating or skipping questions unless the user indicates otherwise.
            4. Provide clear, concise, and informative answers to any user questions, but always relate them back to the topic of the current question.
            5. Do not speculate outside of the information provided by the user, the chat history, or the questions from the database.
            6. If the user’s question is unclear, ask clarifying questions without changing the subject.
            7. After answering a user question, continue with the next question from the database in order, unless instructed otherwise.
            8. Maintain a professional, friendly, and engaging tone at all times.

            Questions to ask (do not modify these): 
            {questions}

            Previous chat history (use this to continue the conversation naturally): 
            {chat_history}

            Now continue the conversation.
            """,
        )

        # -------------------- Step 2: Format chat history --------------------
        formatted_chat_history = [
            f"{msg.role}: {msg.message}" for msg in chat_history.messages
        ]
        formatted_chat_history_str = "\n".join(formatted_chat_history)

        # -------------------- Step 2b: Format questions --------------------
        if isinstance(questions, Questions):
            formatted_questions = "\n".join(questions.questions)
        else:
            formatted_questions = "\n".join(questions)

        # Fill template placeholders with actual chat history and questions
        system_prompt = prompt_template.format(
            questions=formatted_questions, chat_history=formatted_chat_history_str
        )

        # -------------------- Step 3: Build LangChain messages --------------------
        messages = [SystemMessage(content=system_prompt)]
        for msg in chat_history.messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.message))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.message))
            else:
                # Skip unknown roles and log a warning
                logger.warning(f"Skipping unknown role: {msg.role}")

        # -------------------- Step 4: Call the LLM --------------------
        try:
            response = await llm.agenerate(messages=[messages])
            response_text = response.generations[0][0].text
        except Exception as e:
            logger.exception("LLM generation failed")
            raise HTTPException(
                status_code=500, detail=f"LLM generation failed: {str(e)}"
            )

        # -------------------- Step 5: Return response --------------------
        logger.info("LLM response generated successfully")
        return ChatBotContinueOutput(
            message=response_text,  # AI-generated message
            role="assistant",  # The role of the message
            timestamp=datetime.utcnow(),  # UTC timestamp
            session_id=session_id
        )
