import sqlite3

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from ..core.config import Settings, get_settings
from ..llm import ProviderHealth, get_llm_provider
from ..storage import ensure_db_directory

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    app_name: str
    environment: str
    status: str


def _build_health_response(settings: Settings) -> HealthResponse:
    return HealthResponse(
        app_name=settings.app_name,
        environment=settings.app_env,
        status="ok",
    )


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return _build_health_response(settings)


class LLMHealthResponse(BaseModel):
    app_name: str
    environment: str
    llm: ProviderHealth


@router.get(
    "/health/llm",
    response_model=LLMHealthResponse,
    summary="LLM provider availability check",
)
async def llm_health_check(settings: Settings = Depends(get_settings)) -> LLMHealthResponse:
    provider = get_llm_provider(settings)
    return LLMHealthResponse(
        app_name=settings.app_name,
        environment=settings.app_env,
        llm=await provider.health_check(),
    )


class ComponentReadiness(BaseModel):
    name: str
    status: str
    detail: str | None = None


class ReadinessResponse(BaseModel):
    app_name: str
    environment: str
    status: str
    components: list[ComponentReadiness]


@router.get(
    "/health/readiness",
    response_model=ReadinessResponse,
    summary="Readiness check for local dependencies (LLM runtime and SQLite)",
)
async def readiness_check(
    response: Response,
    settings: Settings = Depends(get_settings),
) -> ReadinessResponse:
    llm_status = ComponentReadiness(name="llm", status="unavailable")
    sqlite_status = ComponentReadiness(name="sqlite", status="unavailable")

    try:
        provider = get_llm_provider(settings)
        provider_health = await provider.health_check()
        llm_status = ComponentReadiness(
            name="llm",
            status="ok" if provider_health.available else "unavailable",
            detail=provider_health.message,
        )
    except Exception as exc:  # noqa: BLE001
        llm_status = ComponentReadiness(name="llm", status="unavailable", detail=str(exc))

    try:
        db_path = ensure_db_directory(settings.sqlite_db_path)
        with sqlite3.connect(db_path) as connection:
            connection.execute("SELECT 1")
        sqlite_status = ComponentReadiness(name="sqlite", status="ok")
    except Exception as exc:  # noqa: BLE001
        sqlite_status = ComponentReadiness(name="sqlite", status="unavailable", detail=str(exc))

    ready = llm_status.status == "ok" and sqlite_status.status == "ok"
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        app_name=settings.app_name,
        environment=settings.app_env,
        status="ok" if ready else "degraded",
        components=[llm_status, sqlite_status],
    )
