from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    conversation_id: UUID

class MessageUpdate(BaseModel):
    content: str

class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
