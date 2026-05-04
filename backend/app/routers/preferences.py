from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.schemas import UserPreferences, UserPreferencesCreate
from ..models.db_models import UserPreferences as UserPreferencesModel

router = APIRouter(prefix="/preferences", tags=["preferences"])

@router.get("/{user_id}", response_model=UserPreferences)
async def get_preferences(user_id: str, db: Session = Depends(get_db)):
    """Get user preferences"""
    prefs = db.query(UserPreferencesModel).filter(
        UserPreferencesModel.user_id == user_id
    ).first()

    if not prefs:
        # Create default preferences
        prefs = UserPreferencesModel(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)

    return UserPreferences(
        id=prefs.id,
        user_id=prefs.user_id,
        language=prefs.language,
        news_categories=prefs.get_categories(),
        speech_rate=prefs.speech_rate,
        phrase_language=prefs.phrase_language,
        created_at=prefs.created_at,
        updated_at=prefs.updated_at
    )

@router.post("/", response_model=UserPreferences)
async def create_or_update_preferences(
    prefs_data: UserPreferencesCreate,
    db: Session = Depends(get_db)
):
    """Create or update user preferences"""
    prefs = db.query(UserPreferencesModel).filter(
        UserPreferencesModel.user_id == prefs_data.user_id
    ).first()

    if prefs:
        prefs.language = prefs_data.language
        prefs.set_categories(prefs_data.news_categories)
        prefs.speech_rate = prefs_data.speech_rate
        prefs.phrase_language = prefs_data.phrase_language
    else:
        prefs = UserPreferencesModel(
            user_id=prefs_data.user_id,
            language=prefs_data.language,
            speech_rate=prefs_data.speech_rate,
            phrase_language=prefs_data.phrase_language
        )
        prefs.set_categories(prefs_data.news_categories)
        db.add(prefs)

    db.commit()
    db.refresh(prefs)

    return UserPreferences(
        id=prefs.id,
        user_id=prefs.user_id,
        language=prefs.language,
        news_categories=prefs.get_categories(),
        speech_rate=prefs.speech_rate,
        phrase_language=prefs.phrase_language,
        created_at=prefs.created_at,
        updated_at=prefs.updated_at
    )
