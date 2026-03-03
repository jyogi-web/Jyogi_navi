from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from services.log_store import ping

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    db: str


@router.get("/health", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """サービスの死活監視エンドポイント。"""
    db_status = "ok" if await ping(session) else "unreachable"
    return HealthResponse(status="ok", db=db_status)
