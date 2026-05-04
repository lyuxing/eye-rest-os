import os
import json
from typing import Optional, Dict, Any
import httpx

class AIService:
    """AI服务 - 支持多种LLM提供商"""

    def __init__(self):
        # 支持多种API配置
        self.api_type = os.getenv("AI_API_TYPE", "anthropic")  # anthropic / openai / custom
        self.api_key = os.getenv("AI_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
        self.api_base = os.getenv("AI_API_BASE", "https://api.anthropic.com")
        self.model = os.getenv("AI_MODEL", "claude-sonnet-4-6-20250514")

    async def _call_api(self, prompt: str, max_tokens: int = 500) -> str:
        """调用AI API"""
        if not self.api_key:
            # 没有API key时返回模拟内容
            return self._mock_response(prompt)

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/v1/messages",
                    headers=headers,
                    json=payload
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["content"][0]["text"]
                else:
                    return self._mock_response(prompt)
        except Exception as e:
            print(f"AI API error: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """无API时的模拟响应"""
        if "摘要" in prompt or "summarize" in prompt.lower():
            return "这是一条重要新闻的摘要内容，涵盖了关键信息。"
        elif "每日一句" in prompt or "phrase" in prompt.lower():
            return json.dumps({
                "sentence": "Every cloud has a silver lining.",
                "pronunciation": "/ˈevri klaʊd hæz ə ˈsɪlvər ˈlaɪnɪŋ/",
                "meaning": "黑暗中总有一线光明。比喻困难中总有希望。",
                "example": "Don't lose hope. Every cloud has a silver lining."
            }, ensure_ascii=False)
        elif "演讲" in prompt:
            return json.dumps({
                "title": "坚持的力量",
                "content": "成功不在于你有多聪明，而在于你能坚持多久。每一次失败都是通向成功的一步。",
                "key_points": ["坚持是成功的关键", "失败是成长的阶梯", "保持积极心态"]
            }, ensure_ascii=False)
        elif "对话" in prompt:
            return json.dumps({
                "situation": "咖啡店点单",
                "dialogue": [
                    {"speaker": "A", "text": "Good morning! What can I get for you?"},
                    {"speaker": "B", "text": "I'd like a cappuccino, please."},
                    {"speaker": "A", "text": "Would you like any flavor added?"},
                    {"speaker": "B", "text": "No, thanks. Just the regular one."}
                ],
                "vocabulary": ["cappuccino", "flavor", "regular"]
            }, ensure_ascii=False)
        return "AI服务暂不可用"

    async def summarize_news(self, content: str, max_length: int = 100, language: str = "zh") -> str:
        """新闻摘要"""
        prompt = f"""请将以下新闻内容总结为{max_length}字以内的简短摘要，适合语音播报。
        语言：{"中文" if language == "zh" else "English"}

        新闻内容：
        {content}

        摘要："""
        return await self._call_api(prompt, max_tokens=200)

    async def generate_phrase(self, language: str = "en", level: str = "intermediate") -> Dict[str, Any]:
        """生成每日一句"""
        level_desc = {
            "beginner": "初级，适合初学者，使用简单词汇和句型",
            "intermediate": "中级，适合有一定基础的学习者",
            "advanced": "高级，使用复杂句型和高级词汇"
        }

        prompt = f"""Generate a daily learning phrase for Chinese speakers.
        Language to learn: {language}
        Difficulty level: {level_desc.get(level, level_desc["intermediate"])}

        Return ONLY valid JSON format (no markdown):
        {{
            "sentence": "the phrase in target language",
            "pronunciation": "phonetic or pinyin reading",
            "meaning": "Chinese translation and usage explanation",
            "example": "an example sentence",
            "level": "{level}"
        }}
        Make it practical and useful for daily conversation."""

        response = await self._call_api(prompt, max_tokens=500)

        try:
            # 尝试解析JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except:
            return {
                "sentence": "Practice makes perfect.",
                "pronunciation": "/ˈpræktɪs meɪks ˈpɜːrfɪkt/",
                "meaning": "熟能生巧。反复练习能掌握技能。",
                "example": "Keep practicing every day. Practice makes perfect!",
                "level": level
            }

    async def generate_speech(self, language: str = "en", level: str = "intermediate") -> Dict[str, Any]:
        """生成每日演讲"""
        level_desc = {
            "beginner": "简单话题，如自我介绍、家庭、爱好",
            "intermediate": "中等话题，如工作、旅行、文化差异",
            "advanced": "复杂话题，如社会问题、科技趋势、哲学思考"
        }

        prompt = f"""Generate a short speech/monologue for language learning.
        Language: {language}
        Level: {level_desc.get(level, level_desc["intermediate"])}

        Return ONLY valid JSON format:
        {{
            "title": "speech title",
            "content": "the speech content (2-3 paragraphs, suitable for reading aloud)",
            "key_points": ["point1", "point2", "point3"],
            "vocabulary": ["word1", "word2", "word3"],
            "level": "{level}"
        }}"""

        response = await self._call_api(prompt, max_tokens=800)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except:
            return {
                "title": "The Power of Persistence",
                "content": "Success is not about how smart you are. It's about how long you can keep going. Every failure is a step toward success. Remember, the only real failure is giving up.",
                "key_points": ["坚持是成功的关键", "失败是成长的阶梯", "永不放弃"],
                "vocabulary": ["persistence", "failure", "success"],
                "level": level
            }

    async def generate_dialogue(self, language: str = "en", level: str = "intermediate") -> Dict[str, Any]:
        """生成每日对话"""
        situations = {
            "beginner": ["greeting", "shopping", "asking for directions"],
            "intermediate": ["restaurant", "travel", "job interview"],
            "advanced": ["negotiation", "debate", "professional discussion"]
        }

        prompt = f"""Generate a daily conversation dialogue for language learning.
        Language: {language}
        Level: {level}
        Pick a practical situation from: {situations.get(level, situations["intermediate"])}

        Return ONLY valid JSON format:
        {{
            "situation": "the situation/context",
            "dialogue": [
                {{"speaker": "A", "text": "first line"}},
                {{"speaker": "B", "text": "response"}},
                {{"speaker": "A", "text": "continue"}},
                {{"speaker": "B", "text": "final response"}}
            ],
            "vocabulary": ["word1", "word2", "word3"],
            "cultural_notes": "brief cultural context if relevant",
            "level": "{level}"
        }}"""

        response = await self._call_api(prompt, max_tokens=600)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except:
            return {
                "situation": "咖啡店点单",
                "dialogue": [
                    {"speaker": "A", "text": "Good morning! What can I get for you?"},
                    {"speaker": "B", "text": "I'd like a cappuccino, please."},
                    {"speaker": "A", "text": "Would you like any flavor added?"},
                    {"speaker": "B", "text": "No, thanks. Just the regular one."}
                ],
                "vocabulary": ["cappuccino", "flavor", "regular"],
                "cultural_notes": "在咖啡店点单时，通常先打招呼，然后礼貌地点单",
                "level": level
            }

ai_service = AIService()
