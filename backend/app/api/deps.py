from functools import lru_cache

from fastapi import Depends

from ..attacks import AttackLibrary
from ..core.config import Settings, get_settings
from ..evaluation import CampaignEvaluator
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
