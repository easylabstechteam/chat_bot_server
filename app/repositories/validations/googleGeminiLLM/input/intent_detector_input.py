# ------------------- IMPORTS -------------------
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# ------------------- INTENT DETECTOR INPUT -------------------
class IntentDetectorInput(BaseModel):
    # The message text from the user that needs intent detection
    message: str = Field(..., description="User's message to detect intent from")

    # The current intent of the user (could be empty or previous intent)
    intent: str = Field(..., description="Current or previous intent of the user")
