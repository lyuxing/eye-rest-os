"""
同时运行Web API和Telegram Bot

使用方法:
    python run_all.py
"""

import sys
import os
import asyncio
import threading

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.telegram_bot import TelegramBotService
import uvicorn

def run_web():
    """运行Web API"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

def run_bot():
    """运行Telegram Bot"""
    db = SessionLocal()
    try:
        bot_service = TelegramBotService(db)
        bot_service.run()
    finally:
        db.close()

def main():
    """同时运行两者"""
    print("=" * 50)
    print("🚀 Eye Rest OS - 启动所有服务")
    print("=" * 50)
    print()
    print("📡 Web API: http://localhost:8000")
    print("🤖 Telegram Bot: 运行中")
    print()
    print("按 Ctrl+C 停止所有服务")
    print("=" * 50)

    # 在后台线程运行Telegram Bot
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # 在主线程运行Web API
    try:
        run_web()
    except KeyboardInterrupt:
        print("\n所有服务已停止")

if __name__ == "__main__":
    main()