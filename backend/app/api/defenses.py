from fastapi import APIRouter
from pydantic import BaseModel

from ..defenses import DefenseDescriptor, list_available_defenses, list_default_guarded_defenses

router = APIRouter(prefix="/defenses", tags=["defenses"])


class DefenseCatalogResponse(BaseModel):
    defenses: list[DefenseDescriptor]


class GuardedDefaultDefensesResponse(BaseModel):
    target_name: str
    default_defenses: list[str]


@router.get("", response_model=DefenseCatalogResponse, summary="List available built-in defenses")
def get_defenses() -> DefenseCatalogResponse:
    return DefenseCatalogResponse(defenses=list_available_defenses())


@router.get(
    "/guarded-defaults",
    response_model=GuardedDefaultDefensesResponse,
    summary="List default defenses used by guarded_chat target",
)
def get_guarded_defaults() -> GuardedDefaultDefensesResponse:
    return GuardedDefaultDefensesResponse(
        target_name="guarded_chat",
        default_defenses=list_default_guarded_defenses(),
    )
