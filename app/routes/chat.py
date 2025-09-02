from fastapi import APIRouter
from repositories.redis_database.redis_repository import RedisRepository
from repositories.google_genai_llm.google_genai_llm import GoogleGeminaiRepository
from routes.validations.input.chat_input import ChatInput
from repositories.validations.redis_database.input.delete_chat_data_input import DeleteChatDataInput
from repositories.validations.redis_database.input.create_chat_data_input import CreateChatDataInput
from repositories.validations.redis_database.input.get_chat_data_input import GetChatDataInput
from repositories.validations.redis_database.input.update_chat_data_input import UpdateChatDataInput


router = APIRouter()

# {
#   "ip_adress_timestamp": "123e4567-e89b-12d3-a456-426614174001",
#     "session_id": "123e4567-e89b-12d3-a456-426614174000",  # UUID generated when chat starts; backend must verify this session exists
#     "message": "Hello, how are you?"                       # User's message; min/max length enforced
# }

# create a middleware that checks if the user id is the same
@router.post("/user/chat", summary="Chat with the LLM and detect intent")
async def chat(user_message: ChatInput):
    # create_response = await RedisRepository.create_chat_data(user_message)
    # step 1 -- save user input into redis database
    await RedisRepository.update_chat_data(user_message)
    # sep 2 --- detect the user intent
    intent_detected = await GoogleGeminaiRepository.intent_detector(
        user_message=user_message
    )
    # step 3 --- get chat history
    chat_history = await RedisRepository.get_chat_data(user_message.session_id)
    llm_response = await GoogleGeminaiRepository.chatbot_continue_conversation(
        session_id=user_message.session_id,
        chat_history=chat_history,
        questions=intent_detected.questions,
    )
    # step 4 --- save the llm response into the redis database
    await RedisRepository.update_chat_data(llm_response)
    # step 5 --- send response to  front end
    return llm_response


# Send message & get bot reply
@router.post("/chats/start")
async def initiate_chat(user_message:ChatInput):
    # from now on, the inputs ar"? dz e just messages and session_ids
    return await RedisRepository.create_chat_data(user_message=user_message)

# Retrieve chat history
@router.post("/chats/get/messages")
async def get_chat_messages(input:GetChatDataInput):
    return await RedisRepository.get_chat_data(session_id=input.session_id)

# Delete a chat session
@router.delete("/chats/delete")
async def delete_chat(input: DeleteChatDataInput):
    return await RedisRepository.delete_chat_data(session_id=input.session_id)

@router.get("/")
async def home():
    return {"msg": "home"}
