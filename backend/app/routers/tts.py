from fastapi import APIRouter, Query
from fastapi.responses import Response
from ..services.tts_service import tts_service

router = APIRouter(prefix="/tts", tags=["tts"])

@router.post("/generate")
async def generate_tts(
    text: str = Query(..., description="要转换的文本"),
    lang: str = Query("zh", description="语言代码"),
    rate: float = Query(1.0, ge=0.5, le=2.0, description="语速"),
    gender: str = Query("female", description="声音性别")
):
    """生成TTS音频，返回base64编码"""
    audio_base64 = await tts_service.generate_speech_base64(text, lang, rate, gender)
    return {
        "audio": audio_base64,
        "format": "mp3",
        "text": text
    }

@router.post("/generate/raw")
async def generate_tts_raw(
    text: str = Query(..., description="要转换的文本"),
    lang: str = Query("zh", description="语言代码"),
    rate: float = Query(1.0, ge=0.5, le=2.0, description="语速"),
    gender: str = Query("female", description="声音性别")
):
    """生成TTS音频，返回原始音频流"""
    audio_data = await tts_service.generate_speech(text, lang, rate, gender)
    return Response(
        content=audio_data,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=tts.mp3"
        }
    )