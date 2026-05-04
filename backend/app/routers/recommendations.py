from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.schemas import UserActionCreate, SuccessResponse
from ..models.db_models import User
from ..services.auth_service import get_current_user
from ..services.news_agent import NewsAgent
from ..services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/feed")
async def get_feed(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个性化新闻feed"""
    agent = NewsAgent(db)
    feed = await agent.get_user_feed(current_user.id, limit)
    return {"news": feed, "personalized": True}


@router.post("/action", response_model=SuccessResponse)
async def record_action(
    action_data: UserActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录用户行为（用于推荐系统）"""
    rec_service = RecommendationService(db)
    rec_service.record_action(
        user_id=current_user.id,
        action_type=action_data.action_type,
        content_type=action_data.content_type,
        content_id=action_data.content_id,
        category=action_data.category
    )
    return SuccessResponse(message="Action recorded")


@router.post("/read/{news_id}", response_model=SuccessResponse)
async def mark_read(
    news_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记新闻已读"""
    agent = NewsAgent(db)
    agent.mark_read(current_user.id, news_id)

    # 记录行为
    rec_service = RecommendationService(db)
    news = db.query(DailyNews).filter(DailyNews.news_id == news_id).first()
    if news:
        rec_service.record_action(
            user_id=current_user.id,
            action_type="view",
            content_type="news",
            content_id=news_id,
            category=news.category
        )

    return SuccessResponse(message="Marked as read")


@router.post("/skip/{news_id}", response_model=SuccessResponse)
async def mark_skipped(
    news_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记新闻跳过"""
    agent = NewsAgent(db)
    agent.mark_skipped(current_user.id, news_id)

    # 记录行为
    rec_service = RecommendationService(db)
    news = db.query(DailyNews).filter(DailyNews.news_id == news_id).first()
    if news:
        rec_service.record_action(
            user_id=current_user.id,
            action_type="skip",
            content_type="news",
            content_id=news_id,
            category=news.category
        )

    return SuccessResponse(message="Marked as skipped")


@router.post("/like/{news_id}", response_model=SuccessResponse)
async def mark_like(
    news_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记新闻喜欢"""
    rec_service = RecommendationService(db)
    news = db.query(DailyNews).filter(DailyNews.news_id == news_id).first()
    if news:
        rec_service.record_action(
            user_id=current_user.id,
            action_type="like",
            content_type="news",
            content_id=news_id,
            category=news.category
        )

    return SuccessResponse(message="Liked")


@router.get("/interests")
async def get_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户兴趣及权重"""
    rec_service = RecommendationService(db)
    interests = rec_service.get_user_interests(current_user.id)
    return interests


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取推荐系统统计"""
    rec_service = RecommendationService(db)
    stats = rec_service.get_recommendation_stats(current_user.id)
    return stats


@router.get("/actions")
async def get_actions(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户行为历史"""
    rec_service = RecommendationService(db)
    actions = rec_service.get_user_actions(current_user.id, limit)
    return {"actions": actions}