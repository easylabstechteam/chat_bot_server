from langchain.chat_models import init_chat_model
from core import config  # import your centralized config

# Raise an error if the Google API key is missing to prevent runtime failures
if not config.GOOGLE_API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY environment variable")

# Initialize the Gemini LLM model from LangChain using the Google GenAI provider
llm = init_chat_model(config.GENIE_MODEL_NAME, model_provider="google_genai")
