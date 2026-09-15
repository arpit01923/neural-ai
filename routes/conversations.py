from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Conversation
from dependencies import get_db
from schemas.conversation import ConversationCreate, Conversation as ConversationSchema
from utils.auth import get_current_user

router = APIRouter(prefix="/conversation", tags=["conversations"], dependencies=[Depends(get_current_user)])

@router.get("", response_model=list[ConversationSchema])
async def get_conversations(user_id: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Conversation)
    if user_id:
        query = query.where(Conversation.user_id == user_id)

    result = await db.execute(query)
    conversations = result.scalars().all()
    return conversations

@router.get("/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conversation = result.scalar_one_or_none()

    if not conversation:
        return {"message": "Conversation not found"}

    return {
        "id": conversation.id,
        "title": conversation.title,
        "messages": sorted(conversation.messages, key=lambda message: message.created_at)
    }

@router.post("", response_model=ConversationSchema)
async def create_conversation(conversation: ConversationCreate, db: AsyncSession = Depends(get_db)):
    new_conversation = Conversation(title=conversation.title, user_id=conversation.user_id)
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    return new_conversation
