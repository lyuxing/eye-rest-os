import os
import uuid
import feedparser
import httpx
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.db_models import DailyNews, UserInterest, UserNewsFeed, User
from ..services.ai_service import ai_service

# RSS新闻源配置
RSS_FEEDS = {
    "tech": [
        {"url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "source": "Ars Technica"},
        {"url": "https://www.reddit.com/r/technology/.rss", "source": "Reddit Technology"},
        {"url": "https://hnrss.org/frontpage", "source": "Hacker News"},
    ],
    "finance": [
        {"url": "https://feeds.bloomberg.com/markets/news.rss", "source": "Bloomberg"},
        {"url": "https://www.reddit.com/r/finance/.rss", "source": "Reddit Finance"},
    ],
    "health": [
        {"url": "https://www.reddit.com/r/health/.rss", "source": "Reddit Health"},
        {"url": "https://feeds.arstechnica.com/arstechnica/science", "source": "Ars Science"},
    ],
    "entertainment": [
        {"url": "https://www.reddit.com/r/entertainment/.rss", "source": "Reddit Entertainment"},
        {"url": "https://www.reddit.com/r/movies/.rss", "source": "Reddit Movies"},
    ],
    "science": [
        {"url": "https://www.reddit.com/r/science/.rss", "source": "Reddit Science"},
        {"url": "https://feeds.arstechnica.com/arstechnica/science", "source": "Ars Science"},
    ],
    "sports": [
        {"url": "https://www.reddit.com/r/sports/.rss", "source": "Reddit Sports"},
        {"url": "https://www.reddit.com/r/soccer/.rss", "source": "Reddit Soccer"},
    ]
}

# 聚合间隔（小时）
AGGREGATION_INTERVAL = int(os.getenv("AGGREGATION_INTERVAL", "6"))


class NewsAgent:
    """新闻聚合智能体 - 按需触发"""

    def __init__(self, db: Session):
        self.db = db
        self.last_aggregation_time: Optional[datetime] = None

    def should_aggregate(self) -> bool:
        """检查是否需要重新聚合"""
        if self.last_aggregation_time is None:
            return True

        # 获取最新的新闻时间
        latest_news = self.db.query(DailyNews).order_by(
            DailyNews.created_at.desc()
        ).first()

        if latest_news is None:
            return True

        time_diff = datetime.utcnow() - latest_news.created_at
        return time_diff > timedelta(hours=AGGREGATION_INTERVAL)

    async def aggregate_news(self, categories: List[str] = None) -> List[DailyNews]:
        """聚合新闻"""
        if categories is None:
            categories = list(RSS_FEEDS.keys())

        all_news = []
        now = datetime.utcnow()

        for category in categories:
            if category not in RSS_FEEDS:
                continue

            for feed_info in RSS_FEEDS[category]:
                items = await self._fetch_rss(feed_info["url"], feed_info["source"], category)
                for item in items:
                    # 检查是否已存在
                    existing = self.db.query(DailyNews).filter(
                        DailyNews.news_id == item["news_id"]
                    ).first()

                    if existing:
                        continue

                    # AI摘要
                    summary = await ai_service.summarize_news(item["detail"], 100, "zh")

                    # AI提取关键词
                    keywords = await self._extract_keywords(item["title"] + " " + item["detail"])

                    news = DailyNews(
                        news_id=item["news_id"],
                        title=item["title"],
                        summary=summary,
                        detail=item["detail"],
                        source=item["source"],
                        category=category,
                        published_date=now,
                    )
                    news.set_keywords(keywords)

                    self.db.add(news)
                    all_news.append(news)

        self.db.commit()
        self.last_aggregation_time = now

        return all_news

    async def _fetch_rss(self, url: str, source: str, category: str) -> List[Dict]:
        """从RSS源获取新闻"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                feed = feedparser.parse(response.text)

            items = []
            for entry in feed.entries[:10]:
                # 清理HTML标签
                summary = entry.get('summary', entry.get('title', ''))
                summary = self._clean_html(summary)

                item = {
                    "news_id": str(uuid.uuid4())[:8],
                    "title": entry.get('title', 'No Title'),
                    "detail": summary[:500],
                    "source": source,
                    "category": category
                }
                items.append(item)

            return items
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return []

    def _clean_html(self, text: str) -> str:
        """移除HTML标签"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    async def _extract_keywords(self, text: str) -> List[str]:
        """AI提取关键词"""
        prompt = f"""从以下新闻内容中提取3-5个关键词，返回JSON数组格式：
        {text[:300]}

        关键词："""

        try:
            response = await ai_service._call_api(prompt, max_tokens=100)
            # 简单解析
            keywords = []
            for word in response.split(','):
                word = word.strip().replace('"', '').replace('[', '').replace(']', '')
                if word and len(word) < 20:
                    keywords.append(word)
            return keywords[:5]
        except:
            return []

    async def get_user_feed(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的个性化新闻feed"""
        # 检查是否需要聚合
        if self.should_aggregate():
            # 获取用户感兴趣的类别
            interests = self.db.query(UserInterest).filter(
                UserInterest.user_id == user_id,
                UserInterest.interest_type == "category"
            ).all()

            categories = [i.interest_value for i in interests] or list(RSS_FEEDS.keys())
            await self.aggregate_news(categories)

        # 获取用户兴趣（类别+关键词）
        user_interests = self.db.query(UserInterest).filter(
            UserInterest.user_id == user_id
        ).all()

        category_weights = {}
        keyword_weights = {}

        for interest in user_interests:
            if interest.interest_type == "category":
                category_weights[interest.interest_value] = interest.weight
            else:
                keyword_weights[interest.interest_value] = interest.weight

        # 获取未读新闻
        unread_feed = self.db.query(UserNewsFeed).filter(
            UserNewsFeed.user_id == user_id,
            UserNewsFeed.is_read == False,
            UserNewsFeed.is_skipped == False
        ).all()

        if unread_feed:
            # 返回已分发的新闻
            news_items = []
            for feed_item in unread_feed[:limit]:
                news = self.db.query(DailyNews).filter(
                    DailyNews.id == feed_item.news_id
                ).first()
                if news:
                    news_items.append(self._format_news(news, feed_item.priority))
            return news_items

        # 需要分发新闻
        all_news = self.db.query(DailyNews).order_by(
            DailyNews.created_at.desc()
        ).limit(50).all()

        # 计算每条新闻的优先级
        scored_news = []
        for news in all_news:
            priority = self._calculate_priority(news, category_weights, keyword_weights)

            # 创建用户feed记录
            feed_item = UserNewsFeed(
                user_id=user_id,
                news_id=news.id,
                priority=priority
            )
            self.db.add(feed_item)

            scored_news.append((news, priority))

        self.db.commit()

        # 按优先级排序
        scored_news.sort(key=lambda x: x[1], reverse=True)

        return [self._format_news(news, priority) for news, priority in scored_news[:limit]]

    def _calculate_priority(
        self,
        news: DailyNews,
        category_weights: Dict[str, float],
        keyword_weights: Dict[str, float]
    ) -> float:
        """计算新闻优先级"""
        priority = 0.5

        # 类别匹配
        if news.category in category_weights:
            priority += category_weights[news.category] * 0.3

        # 关键词匹配
        news_keywords = news.get_keywords()
        for kw in news_keywords:
            if kw in keyword_weights:
                priority += keyword_weights[kw] * 0.1

        # 时效性权重
        hours_old = (datetime.utcnow() - news.created_at).total_seconds() / 3600
        if hours_old < 6:
            priority += 0.2
        elif hours_old < 24:
            priority += 0.1

        return min(priority, 1.0)

    def _format_news(self, news: DailyNews, priority: float) -> Dict[str, Any]:
        """格式化新闻返回"""
        return {
            "id": news.news_id,
            "title": news.title,
            "summary": news.summary,
            "detail": news.detail,
            "source": news.source,
            "category": news.category,
            "keywords": news.get_keywords(),
            "priority": priority
        }

    def mark_read(self, user_id: int, news_id: str) -> bool:
        """标记新闻已读"""
        news = self.db.query(DailyNews).filter(DailyNews.news_id == news_id).first()
        if not news:
            return False

        feed_item = self.db.query(UserNewsFeed).filter(
            UserNewsFeed.user_id == user_id,
            UserNewsFeed.news_id == news.id
        ).first()

        if feed_item:
            feed_item.is_read = True
            self.db.commit()
        return True

    def mark_skipped(self, user_id: int, news_id: str) -> bool:
        """标记新闻跳过"""
        news = self.db.query(DailyNews).filter(DailyNews.news_id == news_id).first()
        if not news:
            return False

        feed_item = self.db.query(UserNewsFeed).filter(
            UserNewsFeed.user_id == user_id,
            UserNewsFeed.news_id == news.id
        ).first()

        if feed_item:
            feed_item.is_skipped = True
            self.db.commit()
        return True