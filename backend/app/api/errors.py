from fastapi import HTTPException, status

from ..orchestration import CampaignRequestError, CampaignTargetResolutionError


def raise_campaign_http_error(exc: Exception) -> None:
    if isinstance(exc, CampaignRequestError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, CampaignTargetResolutionError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc),
    ) from exc
