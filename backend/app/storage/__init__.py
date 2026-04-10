"""SQLite persistence layer for campaign history."""

from .db import ensure_db_directory, get_connection, initialize_database, resolve_db_path
from .repository import CampaignRepository
from .schemas import SaveEvaluatedCampaignRequest, SavedCampaignRecord, SavedCampaignSummary

__all__ = [
    "CampaignRepository",
    "SaveEvaluatedCampaignRequest",
    "SavedCampaignRecord",
    "SavedCampaignSummary",
    "ensure_db_directory",
    "get_connection",
    "initialize_database",
    "resolve_db_path",
]
