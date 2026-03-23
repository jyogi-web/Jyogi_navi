from datetime import datetime

from pydantic import BaseModel, Field


class UsageLogCreate(BaseModel):
    session_id: str = Field(min_length=1)
    tokens: int = Field(ge=1)
    category: str | None = None


class UsageLogResponse(BaseModel):
    id: str
    session_id: str
    tokens: int
    category: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
