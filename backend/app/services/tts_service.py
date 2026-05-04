import edge_tts
import io
import base64
from typing import Optional
from functools import lru_cache
import hashlib

# Edge TTS 语音配置
VOICE_MAP = {
    "zh": {
        "female": "zh-CN-XiaoxiaoNeural",      # 晓晓 - 自然女声
        "male": "zh-CN-YunxiNeural",            # 云希 - 自然男声
    },
    "en": {
        "female": "en-US-JennyNeural",          # Jenny - 自然女声
        "male": "en-US-GuyNeural",              # Guy - 自然男声
    },
    "ja": {
        "female": "ja-JP-NanamiNeural",
        "male": "ja-JP-KeitaNeural",
    },
    "fr": {
        "female": "fr-FR-DeniseNeural",
        "male": "fr-FR-HenriNeural",
    },
    "de": {
        "female": "de-DE-KatjaNeural",
        "male": "de-DE-ConradNeural",
    },
    "es": {
        "female": "es-ES-ElviraNeural",
        "male": "es-ES-AlvaroNeural",
    }
}

# 简单的内存缓存
_tts_cache: dict = {}
_CACHE_MAX_SIZE = 100

class TTSService:
    """Edge TTS 服务"""

    def __init__(self):
        self.default_voice = "female"

    def get_voice(self, lang: str, gender: str = "female") -> str:
        """获取对应语言的语音"""
        # 标准化语言代码
        lang_code = lang.split("-")[0] if "-" in lang else lang
        lang_code = lang_code.lower()

        # 匹配语言
        if lang_code in VOICE_MAP:
            return VOICE_MAP[lang_code].get(gender, VOICE_MAP[lang_code]["female"])

        # 默认返回英文
        return VOICE_MAP["en"]["female"]

    def _get_cache_key(self, text: str, lang: str, rate: float, gender: str) -> str:
        """生成缓存键"""
        content = f"{text}|{lang}|{rate}|{gender}"
        return hashlib.md5(content.encode()).hexdigest()

    async def generate_speech(
        self,
        text: str,
        lang: str = "zh",
        rate: float = 1.0,
        gender: str = "female"
    ) -> bytes:
        """生成语音音频"""
        if not text or not text.strip():
            return b""

        # 检查缓存
        cache_key = self._get_cache_key(text, lang, rate, gender)
        if cache_key in _tts_cache:
            return _tts_cache[cache_key]

        # 获取语音
        voice = self.get_voice(lang, gender)

        # 调整语速 (rate: 0.5-2.0 -> Edge格式)
        rate_percent = int((rate - 1.0) * 100)
        rate_str = f"{rate_percent:+d}%"

        try:
            # 创建通信对象
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate_str
            )

            # 生成音频数据
            audio_data = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])

            result = audio_data.getvalue()

            # 缓存结果
            if len(_tts_cache) < _CACHE_MAX_SIZE:
                _tts_cache[cache_key] = result

            return result
        except Exception as e:
            print(f"TTS Error: {e}")
            return b""

    async def generate_speech_base64(
        self,
        text: str,
        lang: str = "zh",
        rate: float = 1.0,
        gender: str = "female"
    ) -> str:
        """生成base64编码的音频（用于前端直接播放）"""
        audio_data = await self.generate_speech(text, lang, rate, gender)
        if not audio_data:
            return ""
        return base64.b64encode(audio_data).decode("utf-8")

tts_service = TTSService()
