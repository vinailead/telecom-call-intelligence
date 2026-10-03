# Pipeline failure runbook

## Symptom

- `run_batches.py` stopped partway and printed `Sentinel written: outputs/.halted_for_human_review.json`, or
- `run_batches.py` refuses to start and reports a prior halt pending review, or
- a single `run_pipeline.py` run exited non-zero before export.

## Why it halts instead of retrying

Strict failure policy (CLAUDE.md): the first task failure halts the entire run. There is no retry and no config flag that enables one. Do not add one without discussing it first.

## Triage

1. Read the halt record:
   ```bash
   cat outputs/.halted_for_human_review.json
   ```
   `error`, `exit_code` and `elapsed_s` separate a hang (elapsed ≈ the task timeout) from a crash (fast non-zero exit). `tasks_completed_before_halt` lists the batches whose output is already safe.
2. Find the failing stage in the log:
   ```bash
   tail -100 outputs/pipeline.log
   ```
3. Classify:

   | Evidence | Likely cause | Next |
   |----------|--------------|------|
   | `elapsed_s` near the timeout, no error | Provider hang | [provider-outage.md](provider-outage.md) |
   | `BudgetExceededError` | Per-run spend hit `BUDGET_USD` | Review `total_cost_usd` in the manifest before raising it |
   | `QualityGateError` | Pass rate below `MIN_PASS_RATE` | [quality-gate-failure.md](quality-gate-failure.md) |
   | `SecurityViolation` | Input/output sanitiser or scope guard tripped | Inspect the offending call; do not bypass the guard |
   | Missing key / startup validation error | Key not set for `EXTRACTION_MODEL`'s provider | Fix `.env` (never commit it) |

## Recover

1. Fix the cause. Re-run a **3-call smoke test** (`make run`) first.
2. Only then clear the halt and resume:
   ```bash
   python run_batches.py --acknowledge-halt
   ```
   Output from `tasks_completed_before_halt` is kept; check the offsets before re-running so completed batches are not paid for twice.

## Before closing out

- [ ] Root cause identified and written down (issue or commit message)
- [ ] Smoke test passed
- [ ] No half-finished outputs committed (`outputs/*.json|csv` stay gitignored)
