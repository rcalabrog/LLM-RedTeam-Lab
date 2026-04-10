from abc import ABC, abstractmethod

from .schemas import TargetDescriptor, TargetInvocationRequest, TargetInvocationResponse


class TargetExecutionError(Exception):
    """Raised when a target cannot complete an invocation."""


class TargetNotFoundError(TargetExecutionError):
    """Raised when a target name is not registered."""


class TargetApp(ABC):
    """Base interface for target applications under test."""

    target_name: str
    target_mode: str
    defense_mode: str
    description: str

    def descriptor(self) -> TargetDescriptor:
        return TargetDescriptor(
            name=self.target_name,
            mode=self.target_mode,
            defense_mode=self.defense_mode,
            description=self.description,
        )

    @abstractmethod
    async def invoke(self, request: TargetInvocationRequest) -> TargetInvocationResponse:
        """Execute the target behavior for one user input."""
