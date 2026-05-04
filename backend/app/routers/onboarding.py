from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.schemas import OnboardingData, SuccessResponse, UserInterestResponse
from ..models.db_models import User, UserInterest, UserPreferences
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/interests", response_model=SuccessResponse)
async def save_interests(
    data: OnboardingData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存用户兴趣设置"""
    # 清除旧的兴趣
    db.query(UserInterest).filter(UserInterest.user_id == current_user.id).delete()

    # 添加类别兴趣
    for category in data.categories:
        interest = UserInterest(
            user_id=current_user.id,
            interest_type="category",
            interest_value=category,
            weight=1.0
        )
        db.add(interest)

    # 添加关键词兴趣
    for keyword in data.keywords:
        interest = UserInterest(
            user_id=current_user.id,
            interest_type="keyword",
            interest_value=keyword,
            weight=1.0
        )
        db.add(interest)

    # 更新用户偏好
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()

    if prefs:
        prefs.set_categories(data.categories)
        prefs.language = data.language
        prefs.phrase_language = data.phrase_language
        prefs.learning_level = data.learning_level
    else:
        prefs = UserPreferences(
            user_id=current_user.id,
            language=data.language,
            phrase_language=data.phrase_language,
            learning_level=data.learning_level
        )
        prefs.set_categories(data.categories)
        db.add(prefs)

    # 标记onboarding完成
    current_user.onboarding_completed = True

    db.commit()

    return SuccessResponse(message="Interests saved successfully")


@router.get("/interests", response_model=List[UserInterestResponse])
async def get_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户兴趣"""
    interests = db.query(UserInterest).filter(
        UserInterest.user_id == current_user.id
    ).all()

    return [UserInterestResponse(
        id=i.id,
        interest_type=i.interest_type,
        interest_value=i.interest_value,
        weight=i.weight
    ) for i in interests]


@router.get("/categories")
async def get_available_categories():
    """获取可用的新闻类别"""
    return {
        "categories": [
            {"id": "tech", "label": "科技", "label_en": "Tech"},
            {"id": "finance", "label": "财经", "label_en": "Finance"},
            {"id": "health", "label": "健康", "label_en": "Health"},
            {"id": "entertainment", "label": "娱乐", "label_en": "Entertainment"},
            {"id": "science", "label": "科学", "label_en": "Science"},
            {"id": "sports", "label": "体育", "label_en": "Sports"},
        ],
        "suggested_keywords": {
            "tech": ["人工智能", "区块链", "云计算", "新能源"],
            "finance": ["股票", "基金", "投资", "理财"],
            "health": ["养生", "健身", "营养", "心理健康"],
            "entertainment": ["电影", "音乐", "游戏", "综艺"],
            "science": ["太空探索", "生物技术", "环保"],
            "sports": ["足球", "篮球", "网球", "电竞"],
        }
    }
