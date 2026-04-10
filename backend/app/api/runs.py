from fastapi import APIRouter, Depends

from ..core.config import Settings, get_settings
from ..orchestration import (
    AttackSelectionPreview,
    CampaignRunRequest,
    CampaignRunResult,
    RedTeamPipeline,
)
from .deps import get_pipeline
from .errors import raise_campaign_http_error

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post(
    "",
    response_model=CampaignRunResult,
    summary="Execute a red-team campaign run against one target",
)
async def create_run(
    payload: CampaignRunRequest,
    settings: Settings = Depends(get_settings),
    pipeline: RedTeamPipeline = Depends(get_pipeline),
) -> CampaignRunResult:
    try:
        return await pipeline.run_campaign(payload, settings)
    except Exception as exc:  # noqa: BLE001
        raise_campaign_http_error(exc)


@router.post(
    "/preview",
    response_model=AttackSelectionPreview,
    summary="Preview selected attacks for a campaign request without executing",
)
def preview_run(
    payload: CampaignRunRequest,
    pipeline: RedTeamPipeline = Depends(get_pipeline),
) -> AttackSelectionPreview:
    try:
        return pipeline.preview_campaign(payload)
    except Exception as exc:  # noqa: BLE001
        raise_campaign_http_error(exc)
