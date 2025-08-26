from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import json


class ChatInput(BaseModel):
    session_id: Optional[UUID] = Field(..., description="")
    role: str = Field(..., min_length=1, max_length=1000, description="")
    message: str = Field(..., min_length=1, max_length=1000, description="")
    intent: str = Field(..., min_length=1, max_length=1000, description="")
    timestamp: datetime = Field(..., description="")

    def to_json(self) -> str:
        self.session_id = str(self.session_id)
        self.timestamp = str(self.timestamp)
        return json.dumps(self.dict())
