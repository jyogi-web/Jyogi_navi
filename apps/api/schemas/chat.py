"""チャット関連の Pydantic スキーマ。"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """チャットリクエスト。"""

    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    """チャットレスポンス。"""

    answer: str
    tokens_used: int
