"""
Telegram Bot 独立运行脚本

使用方法:
    python run_bot.py

或者与后端一起运行:
    python run_all.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.telegram_bot import TelegramBotService

def main():
    """运行Telegram Bot"""
    print("=" * 50)
    print("🤖 Eye Rest OS Telegram Bot")
    print("=" * 50)
    print()

    db = SessionLocal()
    try:
        bot_service = TelegramBotService(db)
        print("正在启动Bot...")
        bot_service.run()
    except KeyboardInterrupt:
        print("\nBot已停止")
    finally:
        db.close()

if __name__ == "__main__":
    main()
