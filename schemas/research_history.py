from pydantic import BaseModel, Field


class ResearchHistoryItem(BaseModel):
    id: str
    question: str
    created_at: str
    report: dict
    sources: list[dict]


class ResearchHistoryCreate(BaseModel):
    question: str = Field(..., min_length=3)
    report: dict
    sources: list[dict]
