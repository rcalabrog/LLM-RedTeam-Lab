from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.config import Settings, get_settings
from ..llm import LLMProviderError
from ..targets import (
    TargetDescriptor,
    TargetInvocationRequest,
    TargetInvocationResponse,
    TargetNotFoundError,
    get_target,
    list_available_targets,
)

router = APIRouter(prefix="/targets", tags=["targets"])


class TargetListResponse(BaseModel):
    default_target: str
    targets: list[TargetDescriptor]


@router.get("", response_model=TargetListResponse, summary="List available target applications")
def list_targets(settings: Settings = Depends(get_settings)) -> TargetListResponse:
    return TargetListResponse(
        default_target=settings.default_target,
        targets=list_available_targets(),
    )


@router.post(
    "/{target_name}/invoke",
    response_model=TargetInvocationResponse,
    summary="Invoke a target application with one user prompt",
)
async def invoke_target(
    target_name: str,
    payload: TargetInvocationRequest,
    settings: Settings = Depends(get_settings),
) -> TargetInvocationResponse:
    try:
        target = get_target(target_name, settings)
    except TargetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    try:
        return await target.invoke(payload)
    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
