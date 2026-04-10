from enum import Enum

from pydantic import BaseModel, Field


class AttackCategory(str, Enum):
    jailbreak_basic = "jailbreak_basic"
    prompt_injection_direct = "prompt_injection_direct"
    system_prompt_extraction = "system_prompt_extraction"
    policy_bypass = "policy_bypass"
    data_leakage_simulation = "data_leakage_simulation"


class AttackSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AttackDefinition(BaseModel):
    """Single static attack prompt definition for lab usage."""

    attack_id: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9_]+$")
    name: str = Field(min_length=3, max_length=120)
    category: AttackCategory
    description: str = Field(min_length=8, max_length=300)
    prompt: str = Field(min_length=10)
    severity: AttackSeverity
    tags: list[str] = Field(default_factory=list)
    expected_risk_signals: list[str] = Field(default_factory=list)
    notes: str | None = None


class AttackCategoryCount(BaseModel):
    category: AttackCategory
    count: int = Field(ge=0)
