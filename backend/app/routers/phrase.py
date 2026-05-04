from fastapi import APIRouter, Query
from ..models.schemas import PhraseItem
from ..services.phrase_service import phrase_service

router = APIRouter(prefix="/phrase", tags=["phrase"])

@router.get("/daily", response_model=PhraseItem)
async def get_daily_phrase(
    language: str = Query("en"),
    level: str = Query("intermediate"),
    use_ai: bool = Query(True)
):
    """Get the phrase of the day"""
    return await phrase_service.get_daily_phrase(language, level, use_ai)

@router.get("/speech")
async def get_daily_speech(
    language: str = Query("en"),
    level: str = Query("intermediate"),
    use_ai: bool = Query(True)
):
    """Get the speech of the day"""
    return await phrase_service.get_daily_speech(language, level, use_ai)

@router.get("/dialogue")
async def get_daily_dialogue(
    language: str = Query("en"),
    level: str = Query("intermediate"),
    use_ai: bool = Query(True)
):
    """Get the dialogue of the day"""
    return await phrase_service.get_daily_dialogue(language, level, use_ai)

@router.post("/generate", response_model=PhraseItem)
async def generate_phrase(request: dict):
    """Generate a new phrase using AI"""
    language = request.get("language", "en")
    level = request.get("level", "intermediate")
    return await phrase_service.get_daily_phrase(language, level, use_ai=True)

@router.get("/{phrase_id}")
async def get_phrase(phrase_id: str):
    """Get a specific phrase by ID"""
    phrase = await phrase_service.get_phrase_by_id(phrase_id)
    if not phrase:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Phrase not found")
    return phrase

@router.get("/levels/list")
async def get_levels():
    """Get all available learning levels"""
    return phrase_service.get_levels()

@router.get("/languages/list")
async def get_languages():
    """Get all supported languages"""
    return phrase_service.get_languages()
