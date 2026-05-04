from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.game_service import game_service

router = APIRouter(prefix="/game", tags=["game"])

class ChoiceRequest(BaseModel):
    session_id: str
    choice: str

@router.get("/list")
async def get_game_list():
    """Get all available games"""
    return game_service.get_game_list()

@router.post("/{game_id}/start")
async def start_game(game_id: str):
    """Start a new game session"""
    result = game_service.start_game(game_id)
    if "error" in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/choice")
async def make_choice(request: ChoiceRequest):
    """Make a choice in the game"""
    result = game_service.make_choice(request.session_id, request.choice)
    if "error" in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/session/{session_id}")
async def get_game_state(session_id: str):
    """Get current game state"""
    result = game_service.get_scene(session_id)
    if "error" in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.delete("/session/{session_id}")
async def end_game_session(session_id: str):
    """End a game session"""
    return game_service.end_game(session_id)
