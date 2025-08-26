# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from datetime import datetime

# ------------------- INTENT DETECTOR OUTPUT -------------------
class IntentDetectorOutput(BaseModel):
    # The intent that the LLM detected from the user's message
    detected_intent: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="The intent detected by the LLM from the user message"
    )

    # The current or previous intent associated with the user (can be used for context)
    current_intent: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="The current or previous intent of the user"
    )
