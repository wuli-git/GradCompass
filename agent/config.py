"""
LLM 和数据库配置
支持 DeepSeek / 阿里千问 / OpenAI / 本地 Ollama
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

# ============================================================
# 数据库配置
# ============================================================
DB_PATH = str(BASE_DIR / "database" / "xmu_graduate.db")
DB_URI = f"sqlite:///{DB_PATH}"

# ============================================================
# LLM 配置
# ============================================================

# 方案1: DeepSeek (推荐 — 便宜 + 中文好)
LLM_CONFIG = {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "api_key": os.getenv("DEEPSEEK_API_KEY", "sk-proxy-local-61855f460d6b1bf9ac8ba19cc764e0b576c85483232b9f6f"),
    "base_url": "https://api.deepseek.com",
    "temperature": 0,
    "max_tokens": 2000,
}

# 方案2: 阿里百炼/千问
# LLM_CONFIG = {
#     "provider": "qwen",
#     "model": "qwen-turbo",
#     "api_key": os.getenv("DASHSCOPE_API_KEY", ""),
#     "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
#     "temperature": 0,
#     "max_tokens": 2000,
# }

# 方案3: 本地 Ollama (Qwen2.5)
# LLM_CONFIG = {
#     "provider": "ollama",
#     "model": "qwen2.5:7b",
#     "api_key": "ollama",
#     "base_url": "http://localhost:11434/v1",
#     "temperature": 0,
#     "max_tokens": 2000,
# }

# Agent 参数
AGENT_CONFIG = {
    "max_iterations": 8,
    "top_k": 15,
    "verbose": True,
    "handle_parsing_errors": True,
}
