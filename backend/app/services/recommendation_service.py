from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.db_models import UserAction, UserInterest, DailyNews


class RecommendationService:
    """基于用户行为的推荐系统"""

    # 行为权重调整值
    ACTION_WEIGHTS = {
        "view": 0.1,
        "detail": 0.2,
        "like": 0.3,
        "skip": -0.2
    }

    def __init__(self, db: Session):
        self.db = db

    def record_action(
        self,
        user_id: int,
        action_type: str,
        content_type: str,
        content_id: str,
        category: Optional[str] = None
    ) -> bool:
        """记录用户行为"""
        action = UserAction(
            user_id=user_id,
            action_type=action_type,
            content_type=content_type,
            content_id=content_id,
            category=category
        )
        self.db.add(action)
        self.db.commit()

        # 更新兴趣权重
        self._update_interest_weights(user_id, action_type, content_type, content_id, category)

        return True

    def _update_interest_weights(
        self,
        user_id: int,
        action_type: str,
        content_type: str,
        content_id: str,
        category: Optional[str]
    ) -> None:
        """根据用户行为更新兴趣权重"""
        weight_delta = self.ACTION_WEIGHTS.get(action_type, 0)

        if weight_delta == 0:
            return

        # 更新类别权重
        if category:
            self._update_category_weight(user_id, category, weight_delta)

        # 更新关键词权重（从新闻内容提取）
        if content_type == "news":
            news = self.db.query(DailyNews).filter(DailyNews.news_id == content_id).first()
            if news:
                for keyword in news.get_keywords():
                    self._update_keyword_weight(user_id, keyword, weight_delta * 0.5)

    def _update_category_weight(self, user_id: int, category: str, delta: float) -> None:
        """更新类别权重"""
        interest = self.db.query(UserInterest).filter(
            UserInterest.user_id == user_id,
            UserInterest.interest_type == "category",
            UserInterest.interest_value == category
        ).first()

        if interest:
            interest.weight = max(0.1, min(2.0, interest.weight + delta))
        else:
            # 创建新的兴趣记录
            interest = UserInterest(
                user_id=user_id,
                interest_type="category",
                interest_value=category,
                weight=max(0.1, 1.0 + delta)
            )
            self.db.add(interest)

        self.db.commit()

    def _update_keyword_weight(self, user_id: int, keyword: str, delta: float) -> None:
        """更新关键词权重"""
        interest = self.db.query(UserInterest).filter(
            UserInterest.user_id == user_id,
            UserInterest.interest_type == "keyword",
            UserInterest.interest_value == keyword
        ).first()

        if interest:
            interest.weight = max(0.1, min(2.0, interest.weight + delta))
        else:
            interest = UserInterest(
                user_id=user_id,
                interest_type="keyword",
                interest_value=keyword,
                weight=max(0.1, 1.0 + delta)
            )
            self.db.add(interest)

        self.db.commit()

    def get_user_interests(self, user_id: int) -> Dict[str, List[Dict]]:
        """获取用户兴趣及权重"""
        interests = self.db.query(UserInterest).filter(
            UserInterest.user_id == user_id
        ).all()

        categories = []
        keywords = []

        for i in interests:
            item = {
                "value": i.interest_value,
                "weight": i.weight
            }
            if i.interest_type == "category":
                categories.append(item)
            else:
                keywords.append(item)

        return {
            "categories": sorted(categories, key=lambda x: x["weight"], reverse=True),
            "keywords": sorted(keywords, key=lambda x: x["weight"], reverse=True)
        }

    def get_user_actions(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """获取用户行为历史"""
        actions = self.db.query(UserAction).filter(
            UserAction.user_id == user_id
        ).order_by(UserAction.created_at.desc()).limit(limit).all()

        return [{
            "action_type": a.action_type,
            "content_type": a.content_type,
            "content_id": a.content_id,
            "category": a.category,
            "created_at": a.created_at.isoformat()
        } for a in actions]

    def get_recommendation_stats(self, user_id: int) -> Dict:
        """获取推荐系统统计"""
        # 行为统计
        action_stats = self.db.query(
            UserAction.action_type,
            func.count(UserAction.id).label("count")
        ).filter(
            UserAction.user_id == user_id
        ).group_by(UserAction.action_type).all()

        action_counts = {stat.action_type: stat.count for stat in action_stats}

        # 兴趣统计
        interests = self.db.query(UserInterest).filter(
            UserInterest.user_id == user_id
        ).all()

        top_categories = sorted(
            [i for i in interests if i.interest_type == "category"],
            key=lambda x: x.weight,
            reverse=True
        )[:3]

        top_keywords = sorted(
            [i for i in interests if i.interest_type == "keyword"],
            key=lambda x: x.weight,
            reverse=True
        )[:5]

        return {
            "total_actions": sum(action_counts.values()),
            "action_breakdown": action_counts,
            "top_categories": [{"name": i.interest_value, "weight": i.weight} for i in top_categories],
            "top_keywords": [{"name": i.interest_value, "weight": i.weight} for i in top_keywords]
        }
