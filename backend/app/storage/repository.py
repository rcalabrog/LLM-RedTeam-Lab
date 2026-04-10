import json
from datetime import datetime, timezone
from typing import Any

from ..evaluation import AttackEvaluationResult, CampaignEvaluationSummary, EvaluatedCampaignResult
from ..orchestration import CampaignAggregateCounts, CampaignAttackResult, CampaignRunResult
from .db import get_connection, initialize_database
from .schemas import SaveEvaluatedCampaignRequest, SavedCampaignRecord, SavedCampaignSummary


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str | None, default: Any) -> Any:
    if value is None or value == "":
        return default
    return json.loads(value)


class CampaignRepository:
    """SQLite repository for evaluated campaign persistence."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        initialize_database(self._db_path)

    def save_evaluated_campaign(self, payload: SaveEvaluatedCampaignRequest) -> SavedCampaignRecord:
        run_result = payload.run_result
        evaluated_result = payload.evaluated_result

        if run_result.run_id != evaluated_result.run_id:
            raise ValueError("run_result.run_id must match evaluated_result.run_id")

        now_iso = _utcnow_iso()
        summary = evaluated_result.summary

        with get_connection(self._db_path) as connection:
            with connection:
                connection.execute("DELETE FROM attack_raw_results WHERE run_id = ?", (run_result.run_id,))
                connection.execute("DELETE FROM attack_evaluations WHERE run_id = ?", (run_result.run_id,))
                connection.execute("DELETE FROM campaign_metrics WHERE run_id = ?", (run_result.run_id,))
                connection.execute("DELETE FROM campaign_runs WHERE run_id = ?", (run_result.run_id,))

                connection.execute(
                    """
                    INSERT INTO campaign_runs (
                        run_id, campaign_name, target_name, pipeline_state,
                        category_filter, severity_filter, attack_ids_filter_json,
                        enabled_defenses_json, model_override, system_prompt_override_used,
                        stop_on_error, metadata_json, started_at, completed_at,
                        selected_attacks, executed_attacks, succeeded_attacks, failed_attacks,
                        evaluated_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_result.run_id,
                        run_result.campaign_name,
                        run_result.target_name,
                        run_result.state.value,
                        run_result.category_filter.value if run_result.category_filter else None,
                        run_result.severity_filter.value if run_result.severity_filter else None,
                        _json_dumps(run_result.attack_ids_filter),
                        (
                            _json_dumps(run_result.enabled_defenses)
                            if run_result.enabled_defenses is not None
                            else None
                        ),
                        run_result.model_override,
                        1 if run_result.system_prompt_override_used else 0,
                        1 if run_result.stop_on_error else 0,
                        _json_dumps(run_result.metadata),
                        run_result.started_at.isoformat(),
                        run_result.completed_at.isoformat(),
                        run_result.counts.selected_attacks,
                        run_result.counts.executed_attacks,
                        run_result.counts.succeeded_attacks,
                        run_result.counts.failed_attacks,
                        evaluated_result.evaluated_at.isoformat(),
                        now_iso,
                        now_iso,
                    ),
                )

                for attack_index, raw in enumerate(run_result.results):
                    connection.execute(
                        """
                        INSERT INTO attack_raw_results (
                            run_id, attack_index, attack_id, attack_name, category, severity,
                            target_name, target_name_snapshot, defense_mode, attack_prompt_snapshot,
                            attack_description_snapshot, model, response_text, warnings_json, flags_json,
                            execution_status, error_message, execution_metadata_json, started_at, completed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            run_result.run_id,
                            attack_index,
                            raw.attack_id,
                            raw.attack_name,
                            raw.category.value,
                            raw.severity.value,
                            raw.target_name,
                            raw.target_name_snapshot,
                            raw.defense_mode,
                            raw.attack_prompt_snapshot,
                            raw.attack_description_snapshot,
                            raw.model,
                            raw.response_text,
                            _json_dumps(raw.warnings),
                            _json_dumps(raw.flags),
                            raw.execution_status.value,
                            raw.error_message,
                            _json_dumps(raw.execution_metadata.model_dump(mode="json")),
                            raw.started_at.isoformat(),
                            raw.completed_at.isoformat(),
                        ),
                    )

                for attack_index, evaluated in enumerate(evaluated_result.evaluations):
                    connection.execute(
                        """
                        INSERT INTO attack_evaluations (
                            run_id, attack_index, attack_id, attack_name, category, severity,
                            target_name, classification, matched_signals_json, matched_rules_json,
                            reasoning_summary, response_excerpt, source_execution_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            run_result.run_id,
                            attack_index,
                            evaluated.attack_id,
                            evaluated.attack_name,
                            evaluated.category.value,
                            evaluated.severity.value,
                            evaluated.target_name,
                            evaluated.classification.value,
                            _json_dumps([signal.value for signal in evaluated.matched_signals]),
                            _json_dumps(
                                [matched_rule.model_dump(mode="json") for matched_rule in evaluated.matched_rules]
                            ),
                            evaluated.reasoning_summary,
                            evaluated.response_excerpt,
                            evaluated.source_execution_status.value,
                        ),
                    )

                summary_dump = summary.model_dump(mode="json")
                connection.execute(
                    """
                    INSERT INTO campaign_metrics (
                        run_id, total_attacks, success_count, failed_count, ambiguous_count,
                        success_rate_overall, failed_rate_overall, ambiguous_rate_overall,
                        per_category_json, per_severity_json, summary_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_result.run_id,
                        summary.total_attacks,
                        summary.success_count,
                        summary.failed_count,
                        summary.ambiguous_count,
                        summary.success_rate_overall,
                        summary.failed_rate_overall,
                        summary.ambiguous_rate_overall,
                        _json_dumps(summary_dump.get("per_category", [])),
                        _json_dumps(summary_dump.get("per_severity", [])),
                        _json_dumps(summary_dump),
                    ),
                )

        saved = self.get_campaign(run_result.run_id)
        if saved is None:
            raise RuntimeError("Campaign save succeeded but could not be read back from storage.")
        return saved

    def list_campaigns(self, *, limit: int = 100, offset: int = 0) -> list[SavedCampaignSummary]:
        with get_connection(self._db_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    c.run_id,
                    c.campaign_name,
                    c.target_name,
                    c.pipeline_state,
                    c.completed_at,
                    c.evaluated_at,
                    m.total_attacks,
                    m.success_count,
                    m.failed_count,
                    m.ambiguous_count,
                    m.success_rate_overall
                FROM campaign_runs c
                JOIN campaign_metrics m ON m.run_id = c.run_id
                ORDER BY c.completed_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()

        return [SavedCampaignSummary.model_validate(dict(row)) for row in rows]

    def get_campaign(self, run_id: str) -> SavedCampaignRecord | None:
        with get_connection(self._db_path) as connection:
            campaign_row = connection.execute(
                "SELECT * FROM campaign_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if campaign_row is None:
                return None

            raw_rows = connection.execute(
                "SELECT * FROM attack_raw_results WHERE run_id = ? ORDER BY attack_index ASC",
                (run_id,),
            ).fetchall()
            evaluation_rows = connection.execute(
                "SELECT * FROM attack_evaluations WHERE run_id = ? ORDER BY attack_index ASC",
                (run_id,),
            ).fetchall()
            metrics_row = connection.execute(
                "SELECT * FROM campaign_metrics WHERE run_id = ?",
                (run_id,),
            ).fetchone()

        run_results = [
            CampaignAttackResult(
                attack_id=row["attack_id"],
                attack_name=row["attack_name"],
                category=row["category"],
                severity=row["severity"],
                target_name=row["target_name"],
                target_name_snapshot=row["target_name_snapshot"],
                defense_mode=row["defense_mode"],
                attack_prompt_snapshot=row["attack_prompt_snapshot"],
                attack_description_snapshot=row["attack_description_snapshot"],
                model=row["model"],
                response_text=row["response_text"],
                warnings=_json_loads(row["warnings_json"], []),
                flags=_json_loads(row["flags_json"], []),
                execution_status=row["execution_status"],
                error_message=row["error_message"],
                execution_metadata=_json_loads(row["execution_metadata_json"], {}),
                started_at=row["started_at"],
                completed_at=row["completed_at"],
            )
            for row in raw_rows
        ]

        evaluation_results = [
            AttackEvaluationResult(
                attack_id=row["attack_id"],
                attack_name=row["attack_name"],
                category=row["category"],
                severity=row["severity"],
                target_name=row["target_name"],
                classification=row["classification"],
                matched_signals=_json_loads(row["matched_signals_json"], []),
                matched_rules=_json_loads(row["matched_rules_json"], []),
                reasoning_summary=row["reasoning_summary"],
                response_excerpt=row["response_excerpt"],
                source_execution_status=row["source_execution_status"],
            )
            for row in evaluation_rows
        ]

        summary = (
            CampaignEvaluationSummary.model_validate(_json_loads(metrics_row["summary_json"], {}))
            if metrics_row is not None
            else CampaignEvaluationSummary(
                total_attacks=0,
                success_count=0,
                failed_count=0,
                ambiguous_count=0,
                success_rate_overall=0.0,
                failed_rate_overall=0.0,
                ambiguous_rate_overall=0.0,
            )
        )

        run_result = CampaignRunResult(
            run_id=campaign_row["run_id"],
            campaign_name=campaign_row["campaign_name"],
            state=campaign_row["pipeline_state"],
            target_name=campaign_row["target_name"],
            category_filter=campaign_row["category_filter"],
            severity_filter=campaign_row["severity_filter"],
            attack_ids_filter=_json_loads(campaign_row["attack_ids_filter_json"], []),
            stop_on_error=bool(campaign_row["stop_on_error"]),
            model_override=campaign_row["model_override"],
            enabled_defenses=(
                _json_loads(campaign_row["enabled_defenses_json"], [])
                if campaign_row["enabled_defenses_json"] is not None
                else None
            ),
            system_prompt_override_used=bool(campaign_row["system_prompt_override_used"]),
            metadata=_json_loads(campaign_row["metadata_json"], {}),
            started_at=campaign_row["started_at"],
            completed_at=campaign_row["completed_at"],
            counts=CampaignAggregateCounts(
                selected_attacks=campaign_row["selected_attacks"],
                executed_attacks=campaign_row["executed_attacks"],
                succeeded_attacks=campaign_row["succeeded_attacks"],
                failed_attacks=campaign_row["failed_attacks"],
            ),
            results=run_results,
        )

        evaluated_result = EvaluatedCampaignResult(
            run_id=run_result.run_id,
            campaign_name=run_result.campaign_name,
            target_name=run_result.target_name,
            evaluated_at=campaign_row["evaluated_at"],
            source_started_at=run_result.started_at,
            source_completed_at=run_result.completed_at,
            evaluations=evaluation_results,
            summary=summary,
        )

        return SavedCampaignRecord(
            saved_at=campaign_row["updated_at"],
            run_result=run_result,
            evaluated_result=evaluated_result,
        )
