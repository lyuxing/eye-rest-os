from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base
import json

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    language = Column(String, default="zh")
    news_categories = Column(Text, default="[]")  # JSON array
    speech_rate = Column(Float, default=1.0)
    phrase_language = Column(String, default="en")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def get_categories(self):
        return json.loads(self.news_categories)

    def set_categories(self, categories):
        self.news_categories = json.dumps(categories)
