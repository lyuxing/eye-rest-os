from fastapi import APIRouter, Query
from typing import List, Optional
from ..models.schemas import NewsItem
from ..services.news_service import news_service
from ..services.ai_service import ai_service

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/", response_model=List[NewsItem])
async def get_news(
    categories: Optional[List[str]] = Query(None),
    limit: int = Query(5, ge=1, le=20)
):
    """Get news items from RSS feeds, optionally filtered by categories"""
    return await news_service.get_news(categories, limit)

@router.get("/{news_id}", response_model=NewsItem)
async def get_news_item(news_id: str):
    """Get a specific news item by ID"""
    news = await news_service.get_news_by_id(news_id)
    if not news:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="News item not found")
    return news

@router.post("/{news_id}/summarize")
async def summarize_news_item(
    news_id: str,
    max_length: int = Query(100, ge=50, le=300),
    language: str = Query("zh")
):
    """Generate AI summary for a news item"""
    news = await news_service.get_news_by_id(news_id)
    if not news:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="News item not found")

    summary = await ai_service.summarize_news(
        news.detail or news.summary,
        max_length=max_length,
        language=language
    )

    return {
        "news_id": news_id,
        "original_title": news.title,
        "summary": summary,
        "source": news.source
    }
