"""Dify 本地服务与工作流 API 的调用逻辑。"""

from __future__ import annotations

from typing import Any

import requests

from .settings import DEFAULT_DIFY_CHAT_URL, DifySettings


REQUEST_TIMEOUT_SECONDS = 60


def build_question(messages: list[str]) -> str:
    """合并一轮聊天消息，移除空白内容。"""
    return "\n".join(message.strip() for message in messages if message.strip())


def get_dify_reply(messages: list[str]) -> str | None:
    """调用本地 FastAPI 服务，获取 Dify 生成的客服回复。"""
    question = build_question(messages)
    if not question:
        print("Dify 调用已跳过：没有可提交的客户消息。")
        return None

    try:
        response = requests.post(
            DEFAULT_DIFY_CHAT_URL,
            json={"question": question},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Dify 调用失败：{error}")
        return None

    answer = payload.get("answer") if isinstance(payload, dict) else None
    if not isinstance(answer, str) or not answer.strip():
        print("Dify 调用失败：本地接口未返回有效 answer。")
        return None
    return answer.strip()


def run_dify_workflow(question: str) -> str | None:
    """直接调用 Dify 工作流，返回其 text 输出。"""
    settings = DifySettings.from_environment()
    response = requests.post(
        settings.url,
        headers={
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": {"questions": question},
            "response_mode": "blocking",
            "user": "fastapi-user",
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    result: Any = response.json()
    if not isinstance(result, dict):
        return None
    value = result.get("data", {}).get("outputs", {}).get("text")
    return value.strip() if isinstance(value, str) and value.strip() else None
