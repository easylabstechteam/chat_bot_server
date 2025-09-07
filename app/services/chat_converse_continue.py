from repositories.redis_database.redis_repository import RedisRepository
from repositories.google_genai_llm.google_genai_llm import GoogleGeminaiRepository
from routes.validations.input.chat_input import ChatInput


# Handles a single user message in an ongoing chat session.
async def chat_converse_continue (user_message:ChatInput): 
    # Steps:
    # 1. Save the user's message to Redis.
    # 2. Detect the user's intent using Google GeminAI.
    # 3. Retrieve the chat history for context.
    # 4. Generate the LLM response based on chat history and detected intent.
    # 5. Save the LLM response to Redis.
    # 6. Return the LLM response to the frontend.

    # Step 1: Save the incoming user message in Redis
    await RedisRepository.update_chat_data(user_message)

    # Step 2: Detect the user's intent using the AI service
    intent_detected = await GoogleGeminaiRepository.intent_detector(
        user_message=user_message
    )

    # Step 3: Retrieve previous chat messages for context
    chat_history = await RedisRepository.get_chat_data(user_message.session_id)

    # Step 4: Continue conversation with the LLM using context and detected intent
    llm_response = await GoogleGeminaiRepository.chatbot_continue_conversation(
        session_id=user_message.session_id,
        chat_history=chat_history,
        questions=intent_detected.questions,
    )

    # Step 5: Save the LLM's response to Redis
    await RedisRepository.update_chat_data(llm_response)

    # Step 6: Return the AI response to the frontend
    return llm_response
