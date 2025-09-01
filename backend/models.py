from pydantic import BaseModel, Field
from typing import List, Optional

class UserQuery(BaseModel):
    message: str = Field(..., description="User's interests or request.")

class IngestItem(BaseModel):
    title: str
    short_summary: str
    full_summary: str
    tags: Optional[List[str]] = None

class IngestPayload(BaseModel):
    items: List[IngestItem]

class Hit(BaseModel):
    title: str
    score: float
    short_summary: str
    tags: List[str] = []

class ChatResponse(BaseModel):
    recommendation_title: str
    rationale: str
    detailed_summary: str
    used_tools: List[str] = []
    hits: List[Hit] = []
