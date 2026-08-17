"""本地 FastAPI 服务：向闲鱼机器人提供 Dify 回复。"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uvicorn

from .dify import run_dify_workflow
from .settings import ConfigurationError


app = FastAPI(title="Dify 智能客服 API")


class ChatRequest(BaseModel):
    question: str


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, int | str | None]:
    try:
        answer = run_dify_workflow(request.question)
    except ConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail=f"Dify 请求失败：{error}") from error
    except ValueError as error:
        raise HTTPException(status_code=502, detail="Dify 未返回有效 JSON。") from error

    return {"code": 200, "answer": answer}


def run() -> None:
    uvicorn.run("xianyu_customer_service.api:app", host="127.0.0.1", port=8000, reload=False)
