import os
import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from ..models.db_models import User, UserInterest, UserPreferences
from ..services.auth_service import AuthService, create_access_token
from ..services.news_agent import NewsAgent
from ..services.recommendation_service import RecommendationService

# Bot Token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8777498633:AAEXJd9c0otb4zTTBzZCfSDLv4h2RcHp5dY")

# 存储用户会话状态 (telegram_id -> email)
user_sessions = {}

# 存储用户注册流程 (telegram_id -> {"step": "email/password", "email": xxx})
registration_flow = {}


class TelegramBotService:
    """Telegram Bot服务"""

    def __init__(self, db: Session):
        self.db = db
        self.app: Optional[Application] = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        telegram_id = update.effective_user.id

        # 检查是否已绑定账号
        user = self.db.query(User).filter(User.display_name == f"tg_{telegram_id}").first()

        if user:
            user_sessions[telegram_id] = user.email
            await self.show_main_menu(update, context, user)
        else:
            # 新用户，显示欢迎和注册选项
            keyboard = [
                [InlineKeyboardButton("📝 注册新账号", callback_data="register")],
                [InlineKeyboardButton("🔗 绑定已有账号", callback_data="login")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "👋 欢迎来到 Eye Rest OS！\n\n"
                "🎧 这是一个音频优先的健康平台\n"
                "📰 为你推送个性化新闻\n"
                "📚 每日一句语言学习\n\n"
                "请选择：",
                reply_markup=reply_markup
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        help_text = """
📖 *Eye Rest OS Bot 使用指南*

*基本命令:*
/start - 开始使用 / 显示主菜单
/news - 获取个性化新闻
/phrase - 每日一句学习
/settings - 偏好设置
/help - 显示帮助

*导航:*
点击按钮即可操作
支持语音播报内容

*提示:*
- 设置你的兴趣获得更好的推荐
- 每天推送个性化内容
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /news 命令"""
        telegram_id = update.effective_user.id
        user = await self.get_user(telegram_id)

        if not user:
            await update.message.reply_text("请先使用 /start 注册或登录")
            return

        # 获取个性化新闻
        agent = NewsAgent(self.db)
        news = await agent.get_user_feed(user.id, limit=3)

        if not news:
            await update.message.reply_text("暂无新闻，请稍后再试")
            return

        for item in news:
            text = f"📰 *{item['title']}*\n\n{item['summary']}\n\n📍 来源: {item['source']}"
            keyboard = [
                [
                    InlineKeyboardButton("📖 详情", callback_data=f"detail_{item['id']}"),
                    InlineKeyboardButton("⏭️ 跳过", callback_data=f"skip_{item['id']}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

    async def phrase_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /phrase 命令"""
        telegram_id = update.effective_user.id
        user = await self.get_user(telegram_id)

        if not user:
            await update.message.reply_text("请先使用 /start 注册或登录")
            return

        # 获取用户偏好
        prefs = self.db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        language = prefs.phrase_language if prefs else "en"

        # 生成每日一句
        from ..services.ai_service import ai_service
        phrase = await ai_service.generate_phrase(language, "intermediate")

        text = f"📚 *每日一句*\n\n"
        text += f"📝 {phrase['sentence']}\n\n"
        text += f"🔤 {phrase['pronunciation']}\n\n"
        text += f"💡 {phrase['meaning']}\n\n"
        text += f"💬 例句: {phrase['example']}"

        await update.message.reply_text(text, parse_mode='Markdown')

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /settings 命令"""
        telegram_id = update.effective_user.id
        user = await self.get_user(telegram_id)

        if not user:
            await update.message.reply_text("请先使用 /start 注册或登录")
            return

        # 获取用户兴趣
        interests = self.db.query(UserInterest).filter(UserInterest.user_id == user.id).all()
        categories = [i.interest_value for i in interests if i.interest_type == "category"]

        # 显示设置菜单
        keyboard = [
            [InlineKeyboardButton(f"📰 新闻类别 ({len(categories)}项已选)", callback_data="settings_categories")],
            [InlineKeyboardButton("💬 学习语言", callback_data="settings_language")],
            [InlineKeyboardButton("🔗 解除绑定", callback_data="unbind")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("⚙️ *偏好设置*\n\n请选择要修改的项目：", parse_mode='Markdown', reply_markup=reply_markup)

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()

        data = query.data
        telegram_id = update.effective_user.id

        if data == "register":
            registration_flow[telegram_id] = {"step": "email"}
            await query.message.edit_text("请输入你的邮箱地址：")

        elif data == "login":
            registration_flow[telegram_id] = {"step": "login_email"}
            await query.message.edit_text("请输入已注册的邮箱地址：")

        elif data.startswith("detail_"):
            news_id = data.replace("detail_", "")
            # 获取新闻详情
            from ..models.db_models import DailyNews
            news = self.db.query(DailyNews).filter(DailyNews.news_id == news_id).first()
            if news:
                await query.message.reply_text(f"📖 *详情*\n\n{news.detail}", parse_mode='Markdown')

        elif data.startswith("skip_"):
            news_id = data.replace("skip_", "")
            user = await self.get_user(telegram_id)
            if user:
                agent = NewsAgent(self.db)
                agent.mark_skipped(user.id, news_id)
                await query.message.reply_text("已跳过，将优化推荐")

        elif data == "main_menu":
            user = await self.get_user(telegram_id)
            if user:
                await self.show_main_menu(update, context, user, edit=True)

        elif data.startswith("settings_categories"):
            await self.show_category_settings(update, context, telegram_id)

        elif data.startswith("cat_"):
            # 切换类别选择
            category = data.replace("cat_", "")
            user = await self.get_user(telegram_id)
            if user:
                # 检查是否已选择
                existing = self.db.query(UserInterest).filter(
                    UserInterest.user_id == user.id,
                    UserInterest.interest_type == "category",
                    UserInterest.interest_value == category
                ).first()

                if existing:
                    self.db.delete(existing)
                else:
                    new_interest = UserInterest(
                        user_id=user.id,
                        interest_type="category",
                        interest_value=category,
                        weight=1.0
                    )
                    self.db.add(new_interest)

                self.db.commit()
                await self.show_category_settings(update, context, telegram_id, edit=True)

        elif data == "unbind":
            user = await self.get_user(telegram_id)
            if user:
                user.display_name = None
                self.db.commit()
                user_sessions.pop(telegram_id, None)
                await query.message.edit_text("已解除绑定，请使用 /start 重新注册或登录")

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理文本消息"""
        telegram_id = update.effective_user.id
        message = update.message.text

        # 检查是否在注册流程中
        if telegram_id in registration_flow:
            flow = registration_flow[telegram_id]

            if flow["step"] == "email":
                # 验证邮箱格式
                if "@" not in message:
                    await update.message.reply_text("邮箱格式不正确，请重新输入：")
                    return

                flow["email"] = message
                flow["step"] = "password"
                await update.message.reply_text("请设置密码（至少6位）：")

            elif flow["step"] == "password":
                if len(message) < 6:
                    await update.message.reply_text("密码太短，请重新输入（至少6位）：")
                    return

                # 创建账号
                try:
                    auth_service = AuthService(self.db)
                    user = auth_service.register(
                        email=flow["email"],
                        password=message,
                        display_name=f"tg_{telegram_id}"
                    )

                    # 保存Telegram关联
                    user.display_name = f"tg_{telegram_id}"
                    self.db.commit()

                    user_sessions[telegram_id] = user.email
                    registration_flow.pop(telegram_id)

                    await update.message.reply_text("✅ 注册成功！")
                    await self.show_main_menu(update, context, user)

                except ValueError as e:
                    await update.message.reply_text(f"注册失败: {str(e)}")

            elif flow["step"] == "login_email":
                if "@" not in message:
                    await update.message.reply_text("邮箱格式不正确，请重新输入：")
                    return

                flow["email"] = message
                flow["step"] = "login_password"
                await update.message.reply_text("请输入密码：")

            elif flow["step"] == "login_password":
                # 尝试登录
                auth_service = AuthService(self.db)
                try:
                    user, token = auth_service.login(flow["email"], message)

                    # 绑定Telegram账号
                    user.display_name = f"tg_{telegram_id}"
                    self.db.commit()

                    user_sessions[telegram_id] = user.email
                    registration_flow.pop(telegram_id)

                    await update.message.reply_text("✅ 登录成功！")
                    await self.show_main_menu(update, context, user)

                except ValueError as e:
                    await update.message.reply_text(f"登录失败: {str(e)}")

        elif telegram_id in user_sessions:
            # 已登录用户，处理指令
            text = message.lower()
            if text in ["新闻", "news", "📰"]:
                context.args = []
                await self.news_command(update, context)
            elif text in ["每日一句", "phrase", "📚"]:
                await self.phrase_command(update, context)
            elif text in ["设置", "settings", "⚙️"]:
                await self.settings_command(update, context)
            elif text in ["菜单", "menu"]:
                user = await self.get_user(telegram_id)
                if user:
                    await self.show_main_menu(update, context, user)
            else:
                await update.message.reply_text(
                    "我理解你的消息了！\n"
                    "输入 '新闻' 获取最新资讯\n"
                    "输入 '每日一句' 学习新内容\n"
                    "输入 '设置' 管理偏好"
                )

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, edit: bool = False):
        """显示主菜单"""
        keyboard = [
            [
                InlineKeyboardButton("📰 新闻", callback_data="news"),
                InlineKeyboardButton("📚 学习", callback_data="phrase")
            ],
            [
                InlineKeyboardButton("⚙️ 设置", callback_data="settings"),
                InlineKeyboardButton("❓ 帮助", callback_data="help")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f"👋 欢迎, {user.email.split('@')[0]}！\n\n请选择功能："

        if edit:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)

    async def show_category_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, telegram_id: int, edit: bool = False):
        """显示类别设置"""
        user = await self.get_user(telegram_id)
        if not user:
            return

        # 获取当前选择的类别
        interests = self.db.query(UserInterest).filter(
            UserInterest.user_id == user.id,
            UserInterest.interest_type == "category"
        ).all()
        selected = [i.interest_value for i in interests]

        categories = [
            ("tech", "💻 科技"),
            ("finance", "📈 财经"),
            ("health", "🏥 健康"),
            ("entertainment", "🎬 娱乐"),
            ("science", "🔬 科学"),
            ("sports", "⚽ 体育"),
        ]

        keyboard = []
        for cat_id, cat_name in categories:
            marker = "✅ " if cat_id in selected else ""
            keyboard.append([InlineKeyboardButton(f"{marker}{cat_name}", callback_data=f"cat_{cat_id}")])

        keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = "📰 选择你感兴趣的类别："

        if edit:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)

    async def get_user(self, telegram_id: int) -> Optional[User]:
        """根据Telegram ID获取用户"""
        return self.db.query(User).filter(User.display_name == f"tg_{telegram_id}").first()

    def setup(self):
        """设置Bot"""
        self.app = Application.builder().token(BOT_TOKEN).build()

        # 添加处理器
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("news", self.news_command))
        self.app.add_handler(CommandHandler("phrase", self.phrase_command))
        self.app.add_handler(CommandHandler("settings", self.settings_command))
        self.app.add_handler(CallbackQueryHandler(self.callback_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))

    async def run_async(self):
        """异步运行Bot"""
        self.setup()
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        print("🤖 Telegram Bot started!")

        # 保持运行
        while True:
            await asyncio.sleep(1)

    def run(self):
        """运行Bot"""
        asyncio.run(self.run_async())
