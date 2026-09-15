from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from config import settings

from routes.users import router as users_router
from routes.conversations import router as conversations_router
from routes.messages import router as messages_router
from routes.pdf_chat import router as pdf_chat_router
from routes.research import router as research_router

app = FastAPI(title="Neural AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(conversations_router)
app.include_router(messages_router)
app.include_router(pdf_chat_router)
app.include_router(research_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Connected to PostgreSQL"}



