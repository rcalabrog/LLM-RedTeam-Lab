from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..core.config import Settings, get_settings
from ..evaluation import CampaignEvaluator
from ..orchestration import (
    CampaignRunRequest,
    RedTeamPipeline,
)
from ..storage import (
    CampaignRepository,
    SaveEvaluatedCampaignRequest,
    SavedCampaignRecord,
    SavedCampaignSummary,
)
from .deps import get_campaign_evaluator, get_pipeline, get_repository
from .errors import raise_campaign_http_error

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post(
    "/campaigns",
    response_model=SavedCampaignRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Persist one evaluated campaign payload",
)
def save_campaign(
    payload: SaveEvaluatedCampaignRequest,
    repository: CampaignRepository = Depends(get_repository),
) -> SavedCampaignRecord:
    try:
        return repository.save_evaluated_campaign(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/campaigns",
    response_model=list[SavedCampaignSummary],
    summary="List saved campaign summaries",
)
def list_campaigns(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    repository: CampaignRepository = Depends(get_repository),
) -> list[SavedCampaignSummary]:
    return repository.list_campaigns(limit=limit, offset=offset)


@router.get(
    "/campaigns/{run_id}",
    response_model=SavedCampaignRecord,
    summary="Retrieve one saved campaign with raw and evaluated details",
)
def get_campaign(
    run_id: str,
    repository: CampaignRepository = Depends(get_repository),
) -> SavedCampaignRecord:
    campaign = repository.get_campaign(run_id)
    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{run_id}' was not found.",
        )
    return campaign


@router.post(
    "/campaigns/execute-evaluate-save",
    response_model=SavedCampaignRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Execute a campaign, evaluate it, and persist the full result",
)
async def execute_evaluate_save_campaign(
    payload: CampaignRunRequest,
    settings: Settings = Depends(get_settings),
    pipeline: RedTeamPipeline = Depends(get_pipeline),
    evaluator: CampaignEvaluator = Depends(get_campaign_evaluator),
    repository: CampaignRepository = Depends(get_repository),
) -> SavedCampaignRecord:
    try:
        run_result = await pipeline.run_campaign(payload, settings)
    except Exception as exc:  # noqa: BLE001
        raise_campaign_http_error(exc)

    evaluated = evaluator.evaluate_campaign(run_result)
    return repository.save_evaluated_campaign(
        SaveEvaluatedCampaignRequest(
            run_result=run_result,
            evaluated_result=evaluated,
        )
    )
