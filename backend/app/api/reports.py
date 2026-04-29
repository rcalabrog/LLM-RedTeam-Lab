from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from ..reporting import CampaignReportExporter
from ..storage import CampaignRepository
from .deps import get_repository

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/campaigns/{run_id}",
    summary="Export a saved campaign report as JSON or PDF",
)
def export_campaign_report(
    run_id: str,
    format: Literal["json", "pdf"] = Query(default="json"),  # noqa: A002
    repository: CampaignRepository = Depends(get_repository),
) -> Response:
    campaign = repository.get_campaign(run_id)
    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{run_id}' was not found.",
        )

    exporter = CampaignReportExporter()
    if format == "json":
        content = exporter.export_json(campaign)
        media_type = "application/json"
    else:
        content = exporter.export_pdf(campaign)
        media_type = "application/pdf"

    filename = exporter.filename_for(campaign, format)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
