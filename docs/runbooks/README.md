# Operational runbooks

| Situation | Runbook |
|-----------|---------|
| A batch stopped or `run_batches.py` refuses to start | [pipeline-failure.md](pipeline-failure.md) |
| Provider timeouts, 429s, or fallback activity | [provider-outage.md](provider-outage.md) |
| `QualityGateError`, or low QA / data-quality pass rate | [quality-gate-failure.md](quality-gate-failure.md) |

## Ground rules

- **No auto-retry.** `Orchestrator.run()` halts the whole multi-batch run on the first task failure and writes `outputs/.halted_for_human_review.json`. Every later `run_batches.py` invocation is blocked until a human reviews the failure and passes `--acknowledge-halt`. Understand the cause before clearing it — a blind retry of a hung batch is what cost ~$1.8 on 2026-08-09.
- **Real API calls cost money.** `BudgetGuard` hard-stops a run at `BUDGET_USD` (`pipeline/config.py`). Smoke-test with `make run` (3 calls) before a 100-call run.
- **Never print or paste API keys** into issues, logs, or PRs.

## Where to look

| Artifact | What it tells you |
|----------|-------------------|
| `outputs/pipeline.log` | Per-stage log, appended across runs |
| `outputs/.halted_for_human_review.json` | Why the last multi-batch run halted: `task_id`, `offset`, `error`, `exit_code`, `elapsed_s`, `tasks_completed_before_halt` |
| `outputs/run_manifest_<ts>.json` | Per-run counts, `qa_verdict`, `data_quality_pass_rate_pct`, token usage and cost, `insights_source` |
| `outputs/qa_report_<ts>.json` | QA summary, grade split, `data_quality_failure_breakdown`, `low_quality_call_ids` |
| `outputs/decisions_<ts>.json` | Why each agent made each autonomous decision (routing, exclusions, provider choice) |
| `outputs/audit_log_<ts>.json` | Governance audit trail (budget, quality gate, PII) |

Quick health read of the latest run:

```bash
.venv/bin/python -m pipeline.metrics
```

It prints the latest manifest's health summary and any flags (low data-quality pass rate, failed calls, rule-based insights fallback, budget overrun). Read-only; it writes nothing.
