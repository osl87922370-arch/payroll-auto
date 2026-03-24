from fastapi import APIRouter

from app.schemas.settings import RateSettings
from app.services import settings_store

router = APIRouter()


@router.get("/", response_model=RateSettings)
def get_settings():
    """현재 설정을 반환합니다."""
    return settings_store.load_settings()


@router.put("/", response_model=RateSettings)
def update_settings(data: RateSettings):
    """설정을 업데이트합니다."""
    updated = settings_store.update_settings(data.model_dump())
    return updated


@router.post("/reset", response_model=RateSettings)
def reset_settings():
    """설정을 기본값으로 초기화합니다."""
    return settings_store.reset_settings()
