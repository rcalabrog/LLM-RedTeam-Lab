from functools import lru_cache

from fastapi import Depends, HTTPException, status

from ..attacks import AttackLibrary
from ..core.config import Settings, get_settings
from ..evaluation import CampaignEvaluator
from ..llm import ProviderHealth
from ..llm import get_llm_provider
from ..orchestration import RedTeamPipeline
from ..storage import CampaignRepository


@lru_cache
def get_attack_library() -> AttackLibrary:
    return AttackLibrary()


@lru_cache
def get_pipeline() -> RedTeamPipeline:
    return RedTeamPipeline()


@lru_cache
def get_campaign_evaluator() -> CampaignEvaluator:
    return CampaignEvaluator()


@lru_cache
def _build_repository(db_path: str) -> CampaignRepository:
    return CampaignRepository(db_path)


def get_repository(settings: Settings = Depends(get_settings)) -> CampaignRepository:
    return _build_repository(settings.sqlite_db_path)


def _provider_health_detail(health: ProviderHealth) -> str:
    return health.error or health.status


async def require_llm_ready(settings: Settings = Depends(get_settings)) -> None:
    provider = get_llm_provider(settings)
    try:
        health = await provider.health_check()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM runtime unavailable: {exc}",
        ) from exc

    if not health.available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM runtime unavailable: {_provider_health_detail(health)}",
        )
