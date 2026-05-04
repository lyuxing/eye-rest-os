from typing import List, Optional
import uuid
import feedparser
import httpx
from datetime import datetime, timedelta
from ..models.schemas import NewsItem

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
    ]
}

class NewsService:
    def __init__(self):
        self.cache: dict = {}
        self.cache_time: dict = {}
        self.cache_duration = timedelta(hours=1)

    async def fetch_rss(self, url: str, source: str, category: str, limit: int = 5) -> List[NewsItem]:
        """从RSS源获取新闻"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                feed = feedparser.parse(response.text)

            items = []
            for entry in feed.entries[:limit]:
                # 清理HTML标签
                summary = entry.get('summary', entry.get('title', ''))
                summary = self._clean_html(summary)

                item = NewsItem(
                    id=str(uuid.uuid4())[:8],
                    title=entry.get('title', 'No Title'),
                    summary=summary[:200] + "..." if len(summary) > 200 else summary,
                    detail=summary,
                    source=source,
                    category=category
                )
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

    async def get_news(self, categories: List[str] = None, limit: int = 5) -> List[NewsItem]:
        """获取新闻，优先使用缓存"""
        if categories is None:
            categories = ["tech", "health"]

        cache_key = ",".join(sorted(categories))
        now = datetime.now()

        # 检查缓存
        if cache_key in self.cache and cache_key in self.cache_time:
            if now - self.cache_time[cache_key] < self.cache_duration:
                return self.cache[cache_key][:limit]

        # 获取新鲜新闻
        all_news = []
        for category in categories:
            if category in RSS_FEEDS:
                for feed_info in RSS_FEEDS[category]:
                    items = await self.fetch_rss(
                        feed_info["url"],
                        feed_info["source"],
                        category
                    )
                    all_news.extend(items)

        # 按时间排序（如果有pubdate的话）
        # 这里简化处理，直接返回
        self.cache[cache_key] = all_news
        self.cache_time[cache_key] = now

        return all_news[:limit]

    async def get_news_by_id(self, news_id: str) -> Optional[NewsItem]:
        """根据ID获取新闻"""
        for cached_news in self.cache.values():
            for item in cached_news:
                if item.id == news_id:
                    return item
        return None

news_service = NewsService()
