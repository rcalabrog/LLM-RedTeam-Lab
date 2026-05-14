import type React from "react";

import { AttacksNavigationPanel } from "@/components/attacks-navigation-panel";
import { InspectorPanel } from "@/components/inspector-panel";
import { AttackResultRow, CampaignViewModel } from "@/types/ui";

interface ResultsViewProps {
  savedCampaignsSlot: React.ReactNode;
  activeView: CampaignViewModel | null;
  rows: AttackResultRow[];
  selectedAttackId: string | null;
  selectedRow: AttackResultRow | null;
  onSelectAttack: (attackId: string) => void;
}

export function ResultsView({
  savedCampaignsSlot,
  activeView,
  rows,
  selectedAttackId,
  selectedRow,
  onSelectAttack
}: ResultsViewProps) {
  return (
    <div className="mt-3 grid min-h-0 flex-1 grid-cols-[3fr_6fr_3fr] gap-3">
      <div className="h-full min-h-0">{savedCampaignsSlot}</div>

      <div className="h-full min-h-0">
        <InspectorPanel view={activeView} selectedRow={selectedRow} />
      </div>

      <div className="h-full min-h-0">
        <AttacksNavigationPanel
          rows={rows}
          selectedAttackId={selectedAttackId}
          onSelectAttack={onSelectAttack}
        />
      </div>
    </div>
  );
}
