from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import news, phrase, preferences, game, tts, auth, onboarding, recommendations
# 导入所有模型以确保表被创建
from .models.db_models import User, UserPreferences, UserInterest, UserAction, DailyNews, UserNewsFeed

app = FastAPI(
    title="Eye Rest OS API",
    description="Backend API for Eye Rest OS - Audio-first wellness platform",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(phrase.router)
app.include_router(preferences.router)
app.include_router(game.router)
app.include_router(tts.router)
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(recommendations.router)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return {
        "message": "Welcome to Eye Rest OS API",
        "version": "0.2.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
