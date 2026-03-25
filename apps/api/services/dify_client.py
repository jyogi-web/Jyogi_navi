"""Dify Chat API クライアント。"""

import json
from dataclasses import dataclass

import httpx
from fastapi import HTTPException

from config import settings


@dataclass
class DifyResponse:
    """Dify Chat API レスポンス。"""

    answer: str
    tokens_used: int


async def send_chat_message(session_id: str, message: str) -> DifyResponse:
    """Dify Chat API にメッセージを送信して回答を返す。"""
    base = settings.dify_api_base_url.rstrip("/")
    url = (
        f"{base}/chat-messages" if base.endswith("/v1") else f"{base}/v1/chat-messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.dify_api_key.get_secret_value()}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {},
        "query": message,
        "user": session_id,
        "response_mode": "blocking",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Dify API timeout") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="Dify API error") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Dify API unreachable") from exc

    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=502, detail="Dify API returned invalid JSON"
        ) from exc

    answer = data.get("answer", "")
    tokens_used = data.get("metadata", {}).get("usage", {}).get("total_tokens", 0)

    return DifyResponse(answer=answer, tokens_used=tokens_used)
