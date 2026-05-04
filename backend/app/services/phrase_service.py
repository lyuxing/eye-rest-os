from typing import List, Dict, Any, Optional
import uuid
from datetime import date
from ..models.schemas import PhraseItem
from .ai_service import ai_service

class PhraseService:
    """语言学习服务 - 支持多种学习模式和级别"""

    def __init__(self):
        self.level_options = ["beginner", "intermediate", "advanced"]
        self.language_options = ["en", "ja", "fr", "de", "es"]
        self.mode_options = ["phrase", "speech", "dialogue"]

        # 预定义内容作为fallback
        self.phrases = self._generate_phrases()
        self.speeches = self._generate_speeches()
        self.dialogues = self._generate_dialogues()

    def _generate_phrases(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4())[:8],
                "sentence": "The early bird catches the worm.",
                "pronunciation": "/ði ˈɜːrli bɜːrd ˈkætʃɪz ðə wɜːrm/",
                "meaning": "早起的鸟儿有虫吃。意指勤奋的人会获得成功。",
                "example": "Remember, the early bird catches the worm, so let's start early tomorrow.",
                "language": "en",
                "level": "beginner"
            },
            {
                "id": str(uuid.uuid4())[:8],
                "sentence": "Actions speak louder than words.",
                "pronunciation": "/ˈækʃənz spiːk ˈlaʊdər ðæn wɜːrdz/",
                "meaning": "行动胜于言辞。意指实际行动比空谈更重要。",
                "example": "Don't just promise, show results. Actions speak louder than words.",
                "language": "en",
                "level": "intermediate"
            },
            {
                "id": str(uuid.uuid4())[:8],
                "sentence": "The pen is mightier than the sword.",
                "pronunciation": "/ðə pen ɪz ˈmaɪtiər ðæn ðə sɔːrd/",
                "meaning": "笔锋胜于剑锋。意指文字和思想的力量比武力更强大。",
                "example": "Writers can change the world. The pen is mightier than the sword.",
                "language": "en",
                "level": "advanced"
            },
        ]

    def _generate_speeches(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4())[:8],
                "title": "Self Introduction",
                "content": "Hello, my name is John. I'm a software engineer from New York. In my free time, I enjoy reading books and playing basketball. I believe that learning new things every day keeps life interesting.",
                "key_points": ["自我介绍的基本结构", "职业和爱好的表达", "个人信念的表达"],
                "vocabulary": ["engineer", "free time", "believe"],
                "language": "en",
                "level": "beginner"
            },
            {
                "id": str(uuid.uuid4())[:8],
                "title": "The Value of Time",
                "content": "Time is our most precious resource. Unlike money, we cannot earn more time. Each day, we have exactly 24 hours to pursue our dreams, help others, and create memories. The question is: how will you spend your time today?",
                "key_points": ["时间的珍贵性", "时间与金钱的对比", "如何利用时间"],
                "vocabulary": ["precious", "resource", "pursue"],
                "language": "en",
                "level": "intermediate"
            },
            {
                "id": str(uuid.uuid4())[:8],
                "title": "The Impact of Technology on Society",
                "content": "Technology has fundamentally transformed how we live, work, and communicate. While it brings unprecedented convenience and connectivity, it also raises important questions about privacy, human connection, and the future of work. We must embrace innovation while thoughtfully addressing its challenges.",
                "key_points": ["科技的双面性", "隐私与便利的权衡", "人机关系的未来"],
                "vocabulary": ["fundamentally", "unprecedented", "embrace"],
                "language": "en",
                "level": "advanced"
            },
        ]

    def _generate_dialogues(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(uuid.uuid4())[:8],
                "situation": "Greeting and Introduction",
                "dialogue": [
                    {"speaker": "A", "text": "Hi! My name is Tom. Nice to meet you!"},
                    {"speaker": "B", "text": "Hi Tom! I'm Sarah. Nice to meet you too!"},
                    {"speaker": "A", "text": "Where are you from?"},
                    {"speaker": "B", "text": "I'm from Canada. How about you?"}
                ],
                "vocabulary": ["nice to meet you", "where are you from"],
                "cultural_notes": "在英语国家，初次见面时握手和微笑是很常见的",
                "language": "en",
                "level": "beginner"
            },
            {
                "id": str(uuid.uuid4())[:8],
                "situation": "Restaurant Ordering",
                "dialogue": [
                    {"speaker": "A", "text": "Good evening! Are you ready to order?"},
                    {"speaker": "B", "text": "Yes, I'd like the grilled salmon, please."},
                    {"speaker": "A", "text": "Would you like any sides with that?"},
                    {"speaker": "B", "text": "I'll have the roasted vegetables and a glass of white wine."}
                ],
                "vocabulary": ["grilled", "sides", "roasted"],
                "cultural_notes": "在西方餐厅，通常先点主菜，再点配菜和饮品",
                "language": "en",
                "level": "intermediate"
            },
            {
                "id": str(uuid.uuid4())[:8],
                "situation": "Job Interview",
                "dialogue": [
                    {"speaker": "A", "text": "Tell me about a challenging project you've worked on."},
                    {"speaker": "B", "text": "I led a team to implement a new customer service system. We faced tight deadlines and technical hurdles, but through effective collaboration, we delivered on time."},
                    {"speaker": "A", "text": "How did you handle the pressure?"},
                    {"speaker": "B", "text": "I prioritized tasks, delegated effectively, and maintained open communication with stakeholders."}
                ],
                "vocabulary": ["hurdles", "collaboration", "delegated"],
                "cultural_notes": "面试中用具体例子展示能力是关键",
                "language": "en",
                "level": "advanced"
            },
        ]

    async def get_daily_phrase(
        self,
        language: str = "en",
        level: str = "intermediate",
        use_ai: bool = True
    ) -> PhraseItem:
        """获取每日一句"""
        if use_ai:
            try:
                data = await ai_service.generate_phrase(language, level)
                return PhraseItem(
                    id=str(uuid.uuid4())[:8],
                    sentence=data.get("sentence", ""),
                    pronunciation=data.get("pronunciation", ""),
                    meaning=data.get("meaning", ""),
                    example=data.get("example", ""),
                    language=language
                )
            except Exception as e:
                print(f"AI generation failed: {e}")

        # Fallback to predefined content
        filtered = [p for p in self.phrases if p["language"] == language and p["level"] == level]
        if not filtered:
            filtered = [p for p in self.phrases if p["language"] == language]
        if not filtered:
            filtered = self.phrases

        today = date.today()
        index = today.timetuple().tm_yday % len(filtered)
        selected = filtered[index]

        return PhraseItem(**selected)

    async def get_daily_speech(
        self,
        language: str = "en",
        level: str = "intermediate",
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """获取每日演讲"""
        if use_ai:
            try:
                data = await ai_service.generate_speech(language, level)
                data["id"] = str(uuid.uuid4())[:8]
                data["language"] = language
                return data
            except Exception as e:
                print(f"AI generation failed: {e}")

        # Fallback
        filtered = [s for s in self.speeches if s["language"] == language and s["level"] == level]
        if not filtered:
            filtered = [s for s in self.speeches if s["language"] == language]
        if not filtered:
            filtered = self.speeches

        today = date.today()
        index = today.timetuple().tm_yday % len(filtered)
        return filtered[index]

    async def get_daily_dialogue(
        self,
        language: str = "en",
        level: str = "intermediate",
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """获取每日对话"""
        if use_ai:
            try:
                data = await ai_service.generate_dialogue(language, level)
                data["id"] = str(uuid.uuid4())[:8]
                data["language"] = language
                return data
            except Exception as e:
                print(f"AI generation failed: {e}")

        # Fallback
        filtered = [d for d in self.dialogues if d["language"] == language and d["level"] == level]
        if not filtered:
            filtered = [d for d in self.dialogues if d["language"] == language]
        if not filtered:
            filtered = self.dialogues

        today = date.today()
        index = today.timetuple().tm_yday % len(filtered)
        return filtered[index]

    async def get_phrase_by_id(self, phrase_id: str) -> Optional[PhraseItem]:
        """根据ID获取内容"""
        for item in self.phrases + self.speeches + self.dialogues:
            if item.get("id") == phrase_id:
                return item
        return None

    def get_levels(self) -> List[Dict[str, str]]:
        """获取所有学习级别"""
        return [
            {"id": "beginner", "name": "初级", "description": "适合初学者，使用简单词汇和句型"},
            {"id": "intermediate", "name": "中级", "description": "适合有一定基础的学习者"},
            {"id": "advanced", "name": "高级", "description": "使用复杂句型和高级词汇"}
        ]

    def get_languages(self) -> List[Dict[str, str]]:
        """获取支持的语言"""
        return [
            {"id": "en", "name": "英语"},
            {"id": "ja", "name": "日语"},
            {"id": "fr", "name": "法语"},
            {"id": "de", "name": "德语"},
            {"id": "es", "name": "西班牙语"}
        ]

phrase_service = PhraseService()
