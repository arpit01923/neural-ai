import uuid
from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Message
from dependencies import get_db
from schemas.message import MessageCreate, MessageUpdate, Message as MessageSchema
from services.ollama_service import generate_stream
from utils.auth import get_current_user

router = APIRouter(prefix="/message", tags=["messages"], dependencies=[Depends(get_current_user)])

@router.get("", response_model=list[MessageSchema])
async def get_messages(conversation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return messages

@router.post("/create", response_model=MessageSchema)
async def create_messages(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    new_message = Message(role=message.role, content=message.content, conversation_id=message.conversation_id)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

@router.post("/stream")
async def stream_message(content: str = Body(..., embed=True)):
    return StreamingResponse(
        generate_stream(content),
        media_type="text/plain"
    )

@router.put("/{id}", response_model=MessageSchema)
async def update_message(
    id: uuid.UUID,
    payload: MessageUpdate,
    db: AsyncSession = Depends(get_db)
):
    message = await db.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.content = payload.content
    await db.commit()
    await db.refresh(message)
    return message

@router.delete("/{id}", response_model=MessageSchema)
async def delete_message(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    message = await db.get(Message, id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    await db.delete(message)
    await db.commit()
    return message

