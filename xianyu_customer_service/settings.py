"""本地路径与 Dify 环境变量配置。"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILE_DIR = PROJECT_ROOT / "playwright-profile"
DEFAULT_DIFY_CHAT_URL = "http://127.0.0.1:8000/chat"


class ConfigurationError(ValueError):
    """必要的本地配置不存在或不完整。"""


def load_project_environment() -> Path | None:
    """加载根目录 .env，并兼容旧版 dify_fastapi/.env。"""
    for path in (PROJECT_ROOT / ".env", PROJECT_ROOT / "dify_fastapi" / ".env"):
        if path.exists():
            load_dotenv(path, override=False)
            return path
    return None


@dataclass(frozen=True)
class DifySettings:
    url: str
    api_key: str

    @classmethod
    def from_environment(cls) -> "DifySettings":
        load_project_environment()
        url = os.getenv("DIFY_URL", "").strip()
        api_key = os.getenv("DIFY_API_KEY", "").strip()
        if not url or not api_key:
            raise ConfigurationError(
                "缺少 DIFY_URL 或 DIFY_API_KEY。请复制 .env.example 为 .env 后填写配置。"
            )
        return cls(url=url, api_key=api_key)
