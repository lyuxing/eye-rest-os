# Eye Rest OS MVP v0.2

音频优先的眼部休息平台，核心交互为4键导航。

## 功能模块

### 1. 时讯简报
- 真实RSS新闻源（Hacker News、Reddit、Ars Technica等）
- AI摘要功能（支持多种LLM API）
- 类别过滤：科技、财经、健康、娱乐

### 2. 语言学习（三级难度）

**每日一句** - 经典短语学习
- 原句 + 发音 + 释义 + 例句
- 支持：英语、日语、法语、德语、西班牙语

**每日演讲** - 演讲技巧训练
- 内容 + 要点 + 词汇
- 按级别生成适合内容

**每日对话** - 情景对话练习
- 场景对话 + 词汇 + 文化提示
- 真实场景模拟

### 3. 音频游戏
- 森林探险（简单）
- 太空站危机（中等）
- 午夜侦探（困难）
- 完全音频交互，4键选择

### 4. 偏好设置
- 界面语言（中文/英文）
- 新闻类别选择
- 播报语速调节
- 学习语言选择
- 学习级别设置（初级/中级/高级）

## 快速启动

### 后端 (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端 (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

## API文档

启动后端后访问: http://localhost:8000/docs

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React + Vite + Tailwind + Zustand |
| 后端 | FastAPI + SQLite + feedparser |
| 音频 | Web Speech API (TTS) |
| AI | 支持多种LLM API（Anthropic/OpenAI/自定义） |

## 环境变量

```bash
# AI API配置（可选，无API时使用预设内容）
AI_API_TYPE=anthropic  # anthropic / openai / custom
AI_API_KEY=your_key
AI_API_BASE=https://api.anthropic.com
AI_MODEL=claude-sonnet-4-6-20250514
```

## 导航说明

**主菜单**: 1.时讯 2.学习 3.游戏 4.设置

**语言学习**: 1.每日一句 2.每日演讲 3.每日对话 4.返回

**游戏**: 按数字选择游戏，游戏中按1-4选择选项

所有页面按4返回上一级。