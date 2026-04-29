import json
import re
from datetime import datetime, timezone
from typing import Any, Literal

from fpdf import FPDF

from ..storage import SavedCampaignRecord

ReportFormat = Literal["json", "pdf"]


class CampaignReportExporter:
    """Build downloadable campaign report artifacts from persisted campaign records."""

    schema_version = "1.0"

    def build_report_document(self, record: SavedCampaignRecord) -> dict[str, Any]:
        run = record.run_result
        evaluated = record.evaluated_result
        summary = evaluated.summary

        attacks: list[dict[str, Any]] = []
        max_len = max(len(run.results), len(evaluated.evaluations))
        for index in range(max_len):
            raw = run.results[index] if index < len(run.results) else None
            evaluation = evaluated.evaluations[index] if index < len(evaluated.evaluations) else None
            attack_id = evaluation.attack_id if evaluation is not None else raw.attack_id if raw is not None else ""
            attack_name = (
                evaluation.attack_name
                if evaluation is not None
                else raw.attack_name
                if raw is not None
                else ""
            )

            attacks.append(
                {
                    "index": index,
                    "attack_id": attack_id,
                    "attack_name": attack_name,
                    "category": _dump_value(
                        evaluation.category if evaluation is not None else raw.category if raw is not None else None
                    ),
                    "severity": _dump_value(
                        evaluation.severity if evaluation is not None else raw.severity if raw is not None else None
                    ),
                    "classification": _dump_value(evaluation.classification if evaluation is not None else None),
                    "reasoning_summary": evaluation.reasoning_summary if evaluation is not None else None,
                    "matched_signals": _dump_value(
                        evaluation.matched_signals if evaluation is not None else []
                    ),
                    "matched_rules": _dump_value(evaluation.matched_rules if evaluation is not None else []),
                    "source_execution_status": _dump_value(
                        evaluation.source_execution_status if evaluation is not None else None
                    ),
                    "response_excerpt": evaluation.response_excerpt if evaluation is not None else None,
                    "execution": _dump_value(raw) if raw is not None else None,
                    "attack_prompt": raw.attack_prompt_snapshot if raw is not None else None,
                    "response": raw.response_text if raw is not None else None,
                    "warnings": raw.warnings if raw is not None else [],
                    "flags": raw.flags if raw is not None else [],
                    "error_message": raw.error_message if raw is not None else None,
                }
            )

        return {
            "schema_version": self.schema_version,
            "report_type": "campaign_run",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "campaign": {
                "run_id": run.run_id,
                "campaign_name": run.campaign_name,
                "target_name": run.target_name,
                "state": _dump_value(run.state),
                "selected_defenses": run.enabled_defenses or [],
                "model_override": run.model_override,
                "system_prompt_override_used": run.system_prompt_override_used,
                "stop_on_error": run.stop_on_error,
                "filters": {
                    "category": _dump_value(run.category_filter),
                    "severity": _dump_value(run.severity_filter),
                    "attack_ids": run.attack_ids_filter,
                },
                "metadata": run.metadata,
                "timestamps": {
                    "started_at": _dump_value(run.started_at),
                    "completed_at": _dump_value(run.completed_at),
                    "evaluated_at": _dump_value(evaluated.evaluated_at),
                    "saved_at": _dump_value(record.saved_at),
                },
                "counts": _dump_value(run.counts),
            },
            "metrics": _dump_value(summary),
            "breakdowns": {
                "category": _dump_value(summary.per_category),
                "severity": _dump_value(summary.per_severity),
            },
            "attacks": attacks,
        }

    def export_json(self, record: SavedCampaignRecord) -> bytes:
        return json.dumps(
            self.build_report_document(record),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")

    def export_pdf(self, record: SavedCampaignRecord) -> bytes:
        document = self.build_report_document(record)
        campaign = document["campaign"]
        metrics = document["metrics"]

        pdf = CampaignReportPdf()
        pdf.set_auto_page_break(auto=True, margin=14)
        pdf.add_page()

        pdf.report_title("LLM Red Team Lab Campaign Report")
        pdf.key_values(
            [
                ("Campaign", campaign["campaign_name"]),
                ("Run ID", campaign["run_id"]),
                ("Target", campaign["target_name"]),
                ("State", campaign["state"]),
                ("Started", campaign["timestamps"]["started_at"]),
                ("Completed", campaign["timestamps"]["completed_at"]),
                ("Evaluated", campaign["timestamps"]["evaluated_at"]),
                ("Selected defenses", ", ".join(campaign["selected_defenses"]) or "None"),
            ]
        )

        pdf.section("Summary Metrics")
        pdf.key_values(
            [
                ("Total attacks", str(metrics["total_attacks"])),
                ("Offensive success", f"{metrics['success_count']} ({_percent(metrics['success_rate_overall'])})"),
                ("Defended / failed", f"{metrics['failed_count']} ({_percent(metrics['failed_rate_overall'])})"),
                ("Ambiguous", f"{metrics['ambiguous_count']} ({_percent(metrics['ambiguous_rate_overall'])})"),
            ]
        )

        pdf.section("Category Breakdown")
        pdf.table_rows(
            ["Category", "Total", "Success", "Failed", "Ambiguous", "Success rate"],
            [
                [
                    item["category"],
                    str(item["total"]),
                    str(item["success"]),
                    str(item["failed"]),
                    str(item["ambiguous"]),
                    _percent(item["success_rate"]),
                ]
                for item in document["breakdowns"]["category"]
            ],
        )

        pdf.section("Severity Breakdown")
        pdf.table_rows(
            ["Severity", "Total", "Success", "Failed", "Ambiguous", "Success rate"],
            [
                [
                    item["severity"],
                    str(item["total"]),
                    str(item["success"]),
                    str(item["failed"]),
                    str(item["ambiguous"]),
                    _percent(item["success_rate"]),
                ]
                for item in document["breakdowns"]["severity"]
            ],
        )

        pdf.section("Attack Results")
        for attack in document["attacks"]:
            pdf.attack_summary(attack)

        return bytes(pdf.output())

    def filename_for(self, record: SavedCampaignRecord, report_format: ReportFormat) -> str:
        stem = _safe_filename(f"{record.run_result.campaign_name}_{record.run_result.run_id}")
        return f"{stem}_report.{report_format}"


class CampaignReportPdf(FPDF):
    def report_title(self, value: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 17)
        self.multi_cell(0, 9, _pdf_safe(value))
        self.ln(2)

    def section(self, value: str) -> None:
        self.ln(3)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 40, 60)
        self.multi_cell(0, 7, _pdf_safe(value))
        self.set_text_color(0, 0, 0)

    def key_values(self, rows: list[tuple[str, str | None]]) -> None:
        self.set_font("Helvetica", "", 9)
        for label, value in rows:
            self.set_x(self.l_margin)
            self.set_font("Helvetica", "B", 9)
            self.multi_cell(0, 5, _pdf_safe(label))
            self.set_x(self.l_margin)
            self.set_font("Helvetica", "", 9)
            self.multi_cell(0, 5, _pdf_safe(value or "n/a"))
        self.ln(1)

    def table_rows(self, headers: list[str], rows: list[list[str]]) -> None:
        if not rows:
            self.body_text("No data.")
            return

        widths = [48, 22, 24, 24, 26, 30]
        self.set_font("Helvetica", "B", 8)
        for index, header in enumerate(headers):
            self.cell(widths[index], 6, _pdf_safe(header), border=1)
        self.ln()

        self.set_font("Helvetica", "", 8)
        for row in rows:
            for index, value in enumerate(row):
                self.cell(widths[index], 6, _pdf_safe(value), border=1)
            self.ln()
        self.ln(1)

    def attack_summary(self, attack: dict[str, Any]) -> None:
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 10)
        heading = f"{attack['index'] + 1}. {attack['attack_id']} - {attack['attack_name']}"
        self.multi_cell(0, 6, _pdf_safe(heading))

        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 8)
        self.multi_cell(
            0,
            5,
            _pdf_safe(
                " | ".join(
                    [
                        f"Classification: {attack.get('classification') or 'n/a'}",
                        f"Category: {attack.get('category') or 'n/a'}",
                        f"Severity: {attack.get('severity') or 'n/a'}",
                        f"Execution: {attack.get('source_execution_status') or 'n/a'}",
                    ]
                )
            ),
        )
        self.body_text(f"Reasoning: {attack.get('reasoning_summary') or 'n/a'}")
        signals = ", ".join(attack.get("matched_signals") or []) or "None"
        self.body_text(f"Matched signals: {signals}")

        rules = attack.get("matched_rules") or []
        if rules:
            rule_lines = [
                f"{rule.get('rule_id')}: {rule.get('evidence')}"
                for rule in rules[:4]
            ]
            self.body_text("Matched rules: " + " | ".join(rule_lines), max_chars=900)
        else:
            self.body_text("Matched rules: None")

        if attack.get("attack_prompt"):
            self.body_text("Attack prompt: " + attack["attack_prompt"], max_chars=900)
        if attack.get("response"):
            self.body_text("Response: " + attack["response"], max_chars=1100)
        if attack.get("error_message"):
            self.body_text("Error: " + attack["error_message"], max_chars=500)
        self.ln(2)

    def body_text(self, value: str, *, max_chars: int | None = None) -> None:
        text = value if max_chars is None or len(value) <= max_chars else f"{value[: max_chars - 3]}..."
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 8)
        self.multi_cell(0, 4.5, _pdf_safe(text))


def _dump_value(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_dump_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _dump_value(item) for key, item in value.items()}
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "campaign"


def _pdf_safe(value: object) -> str:
    return str(value).encode("latin-1", errors="replace").decode("latin-1")
