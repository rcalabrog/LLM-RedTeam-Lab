from abc import ABC, abstractmethod

from .schemas import (
    DefenseEvent,
    DefenseInputPayload,
    DefenseOutputPayload,
    DefenseStage,
)


class DefenseModule(ABC):
    """Base interface for reusable deterministic defenses."""

    defense_name: str
    stage: DefenseStage

    @abstractmethod
    def apply_input(self, payload: DefenseInputPayload) -> DefenseEvent:
        """Apply defense logic to pre-LLM input/context payload."""

    @abstractmethod
    def apply_output(self, payload: DefenseOutputPayload) -> DefenseEvent:
        """Apply defense logic to post-LLM output payload."""
