# Quality gate failure runbook

Two independent checks can fail. Diagnose them separately — see [`../qa-data-quality-gate.md`](../qa-data-quality-gate.md). A call can score 100/100 on the first and still fail the second.

| Check | Question it answers | Reported as |
|-------|--------------------|-------------|
| **QA Score** (0–100) | Was the extraction well-formed? | `summary.pass_rate_pct`, `avg_score`, `grade_*` |
| **Data Quality Gate** (pass/fail) | Can this call's time data be trusted for cost attribution? | `summary.data_quality_pass_rate_pct`, `data_quality_failure_breakdown` |

## Symptom

- `QualityGateError` — either pass rate fell below `MIN_PASS_RATE` (40%) and the run was stopped, or
- a warning/disclaimer — a pass rate fell below `QUALITY_WARN_RATE` (70%). The run continues, failing calls are excluded from aggregation, and `summary.json` gets an `aht_disclaimer` that the dashboard renders as a banner.

## Triage

```bash
.venv/bin/python -m pipeline.metrics            # latest run's health + flags
ls -t outputs/qa_report_*.json | head -1        # the QA report to open
```

In the QA report, compare `summary.pass_rate_pct` with `summary.data_quality_pass_rate_pct`:

- **QA pass rate low** → extraction itself is failing. Check `top_issues` and `low_quality_call_ids`; look at whether `insights_source` or provider fallback also degraded ([provider-outage.md](provider-outage.md)).
- **Only data-quality rate low** → extraction looks fine but the time data is unreliable. Read `data_quality_failure_breakdown` (phase reconciliation, timestamp ground truth, transcript completeness) and inspect the flagged calls. A truncated source transcript is a data problem, not a model problem.

## Recover

1. Inspect flagged calls before changing anything. Do not lower `MIN_PASS_RATE` / `QUALITY_WARN_RATE` to make a run pass.
2. If the cause is input data, fix or exclude the source rows; if it is the model or prompt, treat it as a code change (prompt/`qa_audit.py` edits need human confirmation and a test).
3. Re-run a 3-call smoke test, then resume as in [pipeline-failure.md](pipeline-failure.md).

## Do not drive decisions from a flagged run

Staffing or cost decisions from a run with a low `data_quality_pass_rate_pct` need the flagged calls reviewed first — the dollar figures are only as good as the transcript completeness and timestamp fidelity.
