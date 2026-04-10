TABLES_SQL: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS campaign_runs (
        run_id TEXT PRIMARY KEY,
        campaign_name TEXT NOT NULL,
        target_name TEXT NOT NULL,
        pipeline_state TEXT NOT NULL,
        category_filter TEXT,
        severity_filter TEXT,
        attack_ids_filter_json TEXT NOT NULL,
        enabled_defenses_json TEXT,
        model_override TEXT,
        system_prompt_override_used INTEGER NOT NULL,
        stop_on_error INTEGER NOT NULL,
        metadata_json TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT NOT NULL,
        selected_attacks INTEGER NOT NULL,
        executed_attacks INTEGER NOT NULL,
        succeeded_attacks INTEGER NOT NULL,
        failed_attacks INTEGER NOT NULL,
        evaluated_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS attack_raw_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        attack_index INTEGER NOT NULL,
        attack_id TEXT NOT NULL,
        attack_name TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        target_name TEXT NOT NULL,
        target_name_snapshot TEXT,
        defense_mode TEXT,
        attack_prompt_snapshot TEXT,
        attack_description_snapshot TEXT,
        model TEXT NOT NULL,
        response_text TEXT NOT NULL,
        warnings_json TEXT NOT NULL,
        flags_json TEXT NOT NULL,
        execution_status TEXT NOT NULL,
        error_message TEXT,
        execution_metadata_json TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT NOT NULL,
        FOREIGN KEY(run_id) REFERENCES campaign_runs(run_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS attack_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        attack_index INTEGER NOT NULL,
        attack_id TEXT NOT NULL,
        attack_name TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        target_name TEXT NOT NULL,
        classification TEXT NOT NULL,
        matched_signals_json TEXT NOT NULL,
        matched_rules_json TEXT NOT NULL,
        reasoning_summary TEXT NOT NULL,
        response_excerpt TEXT,
        source_execution_status TEXT NOT NULL,
        FOREIGN KEY(run_id) REFERENCES campaign_runs(run_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS campaign_metrics (
        run_id TEXT PRIMARY KEY,
        total_attacks INTEGER NOT NULL,
        success_count INTEGER NOT NULL,
        failed_count INTEGER NOT NULL,
        ambiguous_count INTEGER NOT NULL,
        success_rate_overall REAL NOT NULL,
        failed_rate_overall REAL NOT NULL,
        ambiguous_rate_overall REAL NOT NULL,
        per_category_json TEXT NOT NULL,
        per_severity_json TEXT NOT NULL,
        summary_json TEXT NOT NULL,
        FOREIGN KEY(run_id) REFERENCES campaign_runs(run_id) ON DELETE CASCADE
    )
    """,
)

INDEXES_SQL: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_attack_raw_results_run_id ON attack_raw_results(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_attack_evaluations_run_id ON attack_evaluations(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_campaign_runs_completed_at ON campaign_runs(completed_at DESC)",
)
