from pydantic import BaseModel


class DailyCount(BaseModel):
    day: str  # "YYYY-MM-DD"
    count: int


class AdminStatsResponse(BaseModel):
    daily_questions: list[DailyCount]
    total_tokens: int
