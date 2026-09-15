from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ConversationBase(BaseModel):
    title: str
    user_id: UUID

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
