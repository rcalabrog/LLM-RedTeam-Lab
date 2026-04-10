"""Target app abstractions and implementations."""

from .base import TargetApp, TargetExecutionError, TargetNotFoundError
from .guarded_chat_target import GuardedChatTarget
from .registry import get_default_target, get_target, list_available_targets
from .schemas import (
    TargetDescriptor,
    TargetExecutionMetadata,
    TargetInvocationRequest,
    TargetInvocationResponse,
)
from .simple_chat_target import SimpleVulnerableChatTarget

__all__ = [
    "GuardedChatTarget",
    "SimpleVulnerableChatTarget",
    "TargetApp",
    "TargetDescriptor",
    "TargetExecutionError",
    "TargetExecutionMetadata",
    "TargetInvocationRequest",
    "TargetInvocationResponse",
    "TargetNotFoundError",
    "get_default_target",
    "get_target",
    "list_available_targets",
]
