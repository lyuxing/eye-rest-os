from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserPreferencesBase(BaseModel):
    language: str = "zh"
    news_categories: List[str] = ["tech", "health"]
    speech_rate: float = 1.0
    phrase_language: str = "en"

class UserPreferencesCreate(UserPreferencesBase):
    user_id: str

class UserPreferences(UserPreferencesBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NewsItemBase(BaseModel):
    title: str
    summary: str
    detail: Optional[str] = None
    source: str
    category: str

class NewsItem(NewsItemBase):
    id: str

class PhraseItemBase(BaseModel):
    sentence: str
    pronunciation: str
    meaning: str
    example: str
    language: str

class PhraseItem(PhraseItemBase):
    id: str

class PhraseRequest(BaseModel):
    language: str = "en"
    difficulty: Optional[str] = "intermediate"

class NewsSummaryRequest(BaseModel):
    content: str
    max_length: Optional[int] = 100
