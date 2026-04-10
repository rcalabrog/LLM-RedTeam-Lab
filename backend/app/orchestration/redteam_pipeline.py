from ..core.config import Settings
from .runner import CampaignRunner
from .schemas import AttackSelectionPreview, CampaignRunRequest, CampaignRunResult


class RedTeamPipeline:
    """
    Thin orchestration facade for campaign runs.

    Kept intentionally lightweight so future phases can add progress streaming
    and persistence hooks without changing route contracts.
    """

    def __init__(self, *, runner: CampaignRunner | None = None) -> None:
        self._runner = runner or CampaignRunner()

    async def run_campaign(
        self,
        request: CampaignRunRequest,
        settings: Settings,
    ) -> CampaignRunResult:
        return await self._runner.execute(request, settings)

    def preview_campaign(self, request: CampaignRunRequest) -> AttackSelectionPreview:
        attacks = self._runner.preview_selection(request)
        return AttackSelectionPreview(
            selected_attack_ids=[attack.attack_id for attack in attacks],
            selected_count=len(attacks),
            category_filter=request.category,
            severity_filter=request.severity,
        )
