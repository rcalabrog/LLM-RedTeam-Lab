from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from ..attacks import AttackCategoryCount, AttackLibrary
from ..core.config import Settings, get_settings
from ..defenses import DefenseDescriptor, list_available_defenses, list_default_guarded_defenses
from ..evaluation import CampaignEvaluator, EvaluatedCampaignResult
from ..orchestration import CampaignRunRequest, RedTeamPipeline
from ..storage import CampaignRepository, SaveEvaluatedCampaignRequest, SavedCampaignRecord
from ..targets import TargetDescriptor, list_available_targets
from .deps import (
    get_attack_library,
    get_campaign_evaluator,
    get_pipeline,
    get_repository,
    require_llm_ready,
)
from .errors import raise_campaign_http_error

router = APIRouter(prefix="/workflows", tags=["workflows"])


class WorkflowCatalogResponse(BaseModel):
    default_target: str
    targets: list[TargetDescriptor]
    defenses: list[DefenseDescriptor]
    guarded_default_defenses: list[str]
    total_attacks: int = Field(ge=0)
    attack_categories: list[AttackCategoryCount]


@router.get(
    "/catalog",
    response_model=WorkflowCatalogResponse,
    summary="Return consolidated MVP catalog data for frontend initialization",
)
def get_workflow_catalog(
    settings: Settings = Depends(get_settings),
    attack_library: AttackLibrary = Depends(get_attack_library),
) -> WorkflowCatalogResponse:
    category_summary = attack_library.summarize_categories()
    return WorkflowCatalogResponse(
        default_target=settings.default_target,
        targets=list_available_targets(),
        defenses=list_available_defenses(),
        guarded_default_defenses=list_default_guarded_defenses(),
        total_attacks=sum(item.count for item in category_summary),
        attack_categories=category_summary,
    )


@router.post(
    "/execute-evaluate",
    response_model=EvaluatedCampaignResult,
    summary="Execute a campaign and evaluate it in one request",
)
async def execute_evaluate_workflow(
    payload: CampaignRunRequest,
    _llm_ready: None = Depends(require_llm_ready),
    settings: Settings = Depends(get_settings),
    pipeline: RedTeamPipeline = Depends(get_pipeline),
    evaluator: CampaignEvaluator = Depends(get_campaign_evaluator),
) -> EvaluatedCampaignResult:
    try:
        run_result = await pipeline.run_campaign(payload, settings)
    except Exception as exc:  # noqa: BLE001
        raise_campaign_http_error(exc)
    return evaluator.evaluate_campaign(run_result)


@router.post(
    "/execute-evaluate-save",
    response_model=SavedCampaignRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Execute, evaluate, and persist campaign results in one request",
)
async def execute_evaluate_save_workflow(
    payload: CampaignRunRequest,
    _llm_ready: None = Depends(require_llm_ready),
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
