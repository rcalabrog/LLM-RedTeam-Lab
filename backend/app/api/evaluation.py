from fastapi import APIRouter, Depends

from ..core.config import Settings, get_settings
from ..evaluation import CampaignEvaluator, EvaluatedCampaignResult
from ..orchestration import (
    CampaignRunRequest,
    CampaignRunResult,
    RedTeamPipeline,
)
from .deps import get_campaign_evaluator, get_pipeline
from .errors import raise_campaign_http_error

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post(
    "",
    response_model=EvaluatedCampaignResult,
    summary="Evaluate a raw campaign run result using deterministic rules",
)
def evaluate_campaign_payload(
    payload: CampaignRunResult,
    evaluator: CampaignEvaluator = Depends(get_campaign_evaluator),
) -> EvaluatedCampaignResult:
    return evaluator.evaluate_campaign(payload)


@router.post(
    "/execute",
    response_model=EvaluatedCampaignResult,
    summary="Execute a campaign run and evaluate it in one request",
)
async def execute_and_evaluate(
    payload: CampaignRunRequest,
    settings: Settings = Depends(get_settings),
    pipeline: RedTeamPipeline = Depends(get_pipeline),
    evaluator: CampaignEvaluator = Depends(get_campaign_evaluator),
) -> EvaluatedCampaignResult:
    try:
        run_result = await pipeline.run_campaign(payload, settings)
    except Exception as exc:  # noqa: BLE001
        raise_campaign_http_error(exc)

    return evaluator.evaluate_campaign(run_result)
