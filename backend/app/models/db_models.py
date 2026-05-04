from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import json


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    onboarding_completed = Column(Boolean, default=False)

    # 关系
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    interests = relationship("UserInterest", back_populates="user")
    actions = relationship("UserAction", back_populates="user")


class UserPreferences(Base):
    """用户偏好设置"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    language = Column(String, default="zh")
    news_categories = Column(Text, default="[]")  # JSON array
    speech_rate = Column(Float, default=1.0)
    phrase_language = Column(String, default="en")
    learning_level = Column(String, default="intermediate")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="preferences")

    def get_categories(self):
        return json.loads(self.news_categories) if self.news_categories else []

    def set_categories(self, categories):
        self.news_categories = json.dumps(categories)


class UserInterest(Base):
    """用户兴趣（类别+关键词）"""
    __tablename__ = "user_interests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    interest_type = Column(String(20))  # 'category' 或 'keyword'
    interest_value = Column(String(100))  # 类别名或关键词
    weight = Column(Float, default=1.0)  # 兴趣权重
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("User", back_populates="interests")


class UserAction(Base):
    """用户行为记录"""
    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action_type = Column(String(50))  # 'view', 'skip', 'like', 'detail'
    content_type = Column(String(50))  # 'news', 'phrase'
    content_id = Column(String(50))
    category = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("User", back_populates="actions")


class DailyNews(Base):
    """每日新闻缓存"""
    __tablename__ = "daily_news"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(String(50), unique=True, index=True)
    title = Column(Text)
    summary = Column(Text)
    detail = Column(Text)
    source = Column(String(100))
    category = Column(String(50))
    keywords = Column(Text, default="[]")  # JSON array of keywords
    published_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    def get_keywords(self):
        return json.loads(self.keywords) if self.keywords else []

    def set_keywords(self, keywords):
        self.keywords = json.dumps(keywords)


class UserNewsFeed(Base):
    """用户新闻分发"""
    __tablename__ = "user_news_feed"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    news_id = Column(Integer, ForeignKey("daily_news.id"))
    priority = Column(Float, default=0.5)  # 推荐优先级
    is_read = Column(Boolean, default=False)
    is_skipped = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
