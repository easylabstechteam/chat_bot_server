from fastapi import APIRouter
from repositories.redis_database.redis_repository import RedisRepository
from repositories.google_genai_llm.google_genai_llm import GoogleGeminaiRepository
from routes.validations.input.chat_input import ChatInput
from services.converse_and_respond.converse_and_respond import converse_and_respond


router = APIRouter()


# {
# "ip_adress_timestamp": "123e4567-e89b-12d3-a456-426614174001", 
#     "session_id": "123e4567-e89b-12d3-a456-426614174000",  # UUID generated when chat starts; backend must verify this session exists
#     "message": "Hello, how are you?"                       # User's message; min/max length enforced
# }


# create a middleware that checks if the user id is the same
@router.post("/chat", summary="Chat with the LLM and detect intent")
async def chat(user_message: ChatInput):
    response = await converse_and_respond(user_message=user_message)
    return response


# Send message & get bot reply
@router.post("/chats/start")
async def initiate_chat():
    # from now on, the inputs ar"? dz e just messages and session_ids
    return await RedisRepository.create_chat_data()


# Send message & get bot reply
@router.post("/chats/{session_id}/messages")
async def send_message(user_message):
    return await GoogleGeminaiRepository.chatbot_continue_conversation(user_message)


# Retrieve chat history
@router.get("/chats/{session_id}/messages")
async def get_chat_messages(session_id):
    return await RedisRepository.get_chat_data(session_id=session_id)


# Delete a chat session
@router.delete("/chats/{session_id}")
async def delete_chat(session_id):
    return await RedisRepository.delete_chat_data(session_id=session_id)


@router.get("/")
async def home():
    return {"msg": "home"}
