from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ==================== 用户认证 ====================

class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    onboarding_completed: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== 用户偏好 ====================

class UserPreferencesBase(BaseModel):
    language: str = "zh"
    news_categories: List[str] = ["tech", "health"]
    speech_rate: float = 1.0
    phrase_language: str = "en"
    learning_level: str = "intermediate"


class UserPreferencesCreate(UserPreferencesBase):
    pass


class UserPreferencesUpdate(BaseModel):
    language: Optional[str] = None
    news_categories: Optional[List[str]] = None
    speech_rate: Optional[float] = None
    phrase_language: Optional[str] = None
    learning_level: Optional[str] = None


class UserPreferences(UserPreferencesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 用户兴趣 ====================

class InterestCreate(BaseModel):
    interest_type: str  # 'category' or 'keyword'
    interest_value: str


class OnboardingData(BaseModel):
    categories: List[str] = []
    keywords: List[str] = []
    language: str = "zh"
    phrase_language: str = "en"
    learning_level: str = "intermediate"


class UserInterestResponse(BaseModel):
    id: int
    interest_type: str
    interest_value: str
    weight: float

    class Config:
        from_attributes = True


# ==================== 用户行为 ====================

class UserActionCreate(BaseModel):
    action_type: str  # 'view', 'skip', 'like', 'detail'
    content_type: str  # 'news', 'phrase'
    content_id: str
    category: Optional[str] = None


# ==================== 新闻 ====================

class NewsItemBase(BaseModel):
    title: str
    summary: str
    detail: Optional[str] = None
    source: str
    category: str


class NewsItem(NewsItemBase):
    id: str
    keywords: List[str] = []


class NewsSummaryRequest(BaseModel):
    content: str
    max_length: Optional[int] = 100


# ==================== 每日一句 ====================

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


# ==================== 演讲和对话 ====================

class SpeechItemBase(BaseModel):
    title: str
    content: str
    key_points: List[str]
    vocabulary: List[str]
    language: str
    level: str


class SpeechItem(SpeechItemBase):
    id: str


class DialogueItemBase(BaseModel):
    situation: str
    dialogue: List[dict]
    vocabulary: List[str]
    cultural_notes: Optional[str] = None
    language: str
    level: str


class DialogueItem(DialogueItemBase):
    id: str


# ==================== 游戏 ====================

class GameSessionBase(BaseModel):
    session_id: str
    game_id: str
    title: Optional[str] = None
    scene_id: str
    narration: str
    choices: List[dict]
    is_end: bool
    result: Optional[str] = None
    round: int = 1


class GameSession(GameSessionBase):
    pass


class GameInfo(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str


# ==================== 通用响应 ====================

class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
