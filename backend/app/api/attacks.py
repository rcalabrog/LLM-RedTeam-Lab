from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..attacks import AttackCategory, AttackCategoryCount, AttackDefinition, AttackLibrary, AttackSeverity
from .deps import get_attack_library

router = APIRouter(prefix="/attacks", tags=["attacks"])


class AttackSummaryResponse(BaseModel):
    total_attacks: int = Field(ge=0)
    categories: list[AttackCategoryCount]


@router.get("/summary", response_model=AttackSummaryResponse, summary="List attack categories and counts")
def attacks_summary(library: AttackLibrary = Depends(get_attack_library)) -> AttackSummaryResponse:
    categories = library.summarize_categories()
    total = sum(item.count for item in categories)
    return AttackSummaryResponse(total_attacks=total, categories=categories)


@router.get("", response_model=list[AttackDefinition], summary="List attack definitions")
def list_attacks(
    category: AttackCategory | None = Query(default=None),
    severity: AttackSeverity | None = Query(default=None),
    attack_ids: str | None = Query(
        default=None,
        description="Optional comma-separated attack IDs.",
    ),
    library: AttackLibrary = Depends(get_attack_library),
) -> list[AttackDefinition]:
    if attack_ids:
        ids = [item.strip() for item in attack_ids.split(",") if item.strip()]
        attacks = library.get_attacks_by_ids(ids)
    else:
        attacks = library.query_attacks(category=category, severity=severity)

    if category is not None:
        attacks = [attack for attack in attacks if attack.category == category]
    if severity is not None:
        attacks = [attack for attack in attacks if attack.severity == severity]
    return attacks


@router.get("/{attack_id}", response_model=AttackDefinition, summary="Get one attack by ID")
def get_attack(
    attack_id: str,
    library: AttackLibrary = Depends(get_attack_library),
) -> AttackDefinition:
    attack = library.get_attack_by_id(attack_id)
    if attack is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attack '{attack_id}' was not found.",
        )
    return attack
