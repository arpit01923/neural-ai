from pydantic import BaseModel, Field


class ResearchQuery(BaseModel):
    query: str = Field(..., min_length=3, description="Research question to investigate")


class ResearchSection(BaseModel):
    heading: str
    content: str


class ResearchSource(BaseModel):
    title: str
    url: str
    content: str
    score: float


class ResearchResponse(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    sections: list[ResearchSection] = []
    sources: list[ResearchSource]
