# GitHub Readiness Implementation Plan

This file contains:
1. **Claude Code Execution Summary** — what to implement and in what order
2. **Direct Repo Tasks Checklist** — GitHub UI settings to enable
3. **Concrete Patch Plan** — exact files to create/update with sample code

---

## Part 1: Claude Code Execution Summary

### Phase 1: Governance & Documentation (5 files)
Create these files in the repo root and `.github/`:
- `.github/CODEOWNERS`
- `.github/SECURITY.md`
- `CONTRIBUTING.md`
- `.github/dependabot.yml`
- `.pre-commit-config.yaml`

**Time:** ~10 min
**Impact:** Establishes ownership and contributor guidelines

### Phase 2: Operational Infrastructure (2 files)
- `pipeline/metrics.py` — runtime health summary helper
- `docs/runbooks/README.md` — operational runbook index

**Time:** ~15 min
**Impact:** Enables structured health monitoring and troubleshooting

### Phase 3: CI Hardening (1 file)
- Update `.github/workflows/ci.yml` — add coverage gate, mypy, better pip setup

**Time:** ~10 min
**Impact:** Prevents regressions and silent untested code

### Phase 4: Dev Convenience (1 file)
- `Makefile` — standardized test/lint commands

**Time:** ~5 min
**Impact:** Simplifies local workflow and CI consistency

**Total implementation time:** ~40 min for all code changes

---

## Part 2: Direct Repo Tasks Checklist

These must be done in GitHub UI (not in code):

- [ ] Go to repo Settings → Branches
  - [ ] Enable "Require a pull request before merging"
  - [ ] Enable "Require approvals"
  - [ ] Set "Required number of approvals before merging" to **1**
  - [ ] Enable "Dismiss stale pull request approvals when new commits are pushed"
  - [ ] Enable "Require status checks to pass before merging"
  - [ ] Select required checks:
    - [ ] `Semgrep security scan`
    - [ ] `Test (Python 3.11)`
    - [ ] `Test (Python 3.12)`
  - [ ] Enable "Require branches to be up to date before merging"
  - [ ] Enable "Restrict who can push to matching branches" (optionally)

- [ ] Go to repo Settings → Security → Code security and analysis
  - [ ] Enable "Dependabot alerts" (if available)
  - [ ] Enable "Dependabot security updates" (if available)
  - [ ] Enable "Secret scanning" (if available)
  - [ ] Confirm "GitHub Advanced Security" status

- [ ] Go to repo Settings → Code security → Secrets
  - [ ] Verify `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `NVIDIA_API_KEY` are stored as repo secrets

- [ ] Go to repo Settings → Environments (optional, for production safety)
  - [ ] Create "production" environment
  - [ ] Require approval before deployment

**Total UI setup time:** ~10 min

---

## Part 3: Concrete Patch Plan

### 3.1 `.github/CODEOWNERS`
**Purpose:** Define ownership for PR reviews
**Action:** Create new file

```text
* @vindon
pipeline/ @vindon
tests/ @vindon
.github/ @vindon
docs/ @vindon
```

---

### 3.2 `.github/SECURITY.md`
**Purpose:** Security reporting policy
**Action:** Create new file

```md
# Security Policy

## Reporting a vulnerability

Please report security issues **privately** by:
1. Using GitHub Security Advisories (preferred)
2. Emailing the maintainer
3. Using GitHub's private vulnerability reporting

**Do not open public issues for security vulnerabilities.**

## Supported versions

The project supports the latest `main` branch and the latest release tag.

## Disclosure timeline

- Initial report received → acknowledged within 24 hours
- Investigation → 7 days
- Fix released → disclosed within 30 days of initial report

---

## Security considerations

This project uses:
- LLM API keys (Anthropic, NVIDIA, Gemini) — store in repo secrets, never in code
- LangGraph for orchestration — keep LangSmith observability keys in `.env` only
- Langfuse tracing — optional, keyed via environment variables
- HuggingFace dataset access — use `huggingface_hub` with explicit token management

All API keys must be managed via GitHub Secrets or `.env` files, never hardcoded.
```

---

### 3.3 `CONTRIBUTING.md`
**Purpose:** Developer onboarding and contribution guidelines
**Action:** Create new file

```md
# Contributing

Thanks for your interest in contributing to the telecom call intelligence pipeline!

## Quick start

### Setup
```bash
git clone https://github.com/vindon/telecom-call-intelligence
cd telecom-call-intelligence

python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Pre-commit hooks (recommended)
```bash
pre-commit install
pre-commit run --all-files  # test hooks locally
```

### Run checks locally
```bash
make lint    # ruff check + formatting
make test    # pytest with coverage
make check   # lint + test (recommended before push)
```

## Development workflow

1. Create a branch from `main`
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make changes and ensure all checks pass
   ```bash
   make check
   ```

3. Commit with clear messages
   ```bash
   git commit -m "Add feature: description of what changed"
   ```

4. Push and open a pull request
   ```bash
   git push origin feature/your-feature
   ```

5. PR must pass CI and receive at least one review before merge

## Code guidelines

- **Linting:** all code must pass `ruff check`
- **Formatting:** run `ruff format` before commit
- **Type hints:** new code should include type hints where practical
- **Tests:** behavioral changes should include tests
- **Coverage:** maintain ≥80% coverage on `pipeline/` module
- **Logging:** use `pipeline.logger.get_logger(__name__)` for consistent logs
- **Config:** use `pipeline.config` for all constants; never hardcode

## Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run only fast tests (skip slow/integration)
```bash
pytest tests/ -m "not slow and not integration"
```

### Run with coverage
```bash
pytest tests/ --cov=pipeline --cov-report=term-missing --cov-fail-under=80
```

### Run a specific test
```bash
pytest tests/test_analyzer.py::test_extraction_flow -v
```

## Pull request checklist

Before submitting:
- [ ] Branch is based on latest `main`
- [ ] All tests pass locally: `make check`
- [ ] Coverage is ≥80%: `make test`
- [ ] Commits are clean and descriptive
- [ ] No hardcoded secrets or API keys
- [ ] Docstrings added for new functions/modules
- [ ] Changes logged in `CHANGELOG.md` (if applicable)

## Questions or issues?

Open a GitHub issue or discussion, or reach out to @vindon.
```

---

### 3.4 `.github/dependabot.yml`
**Purpose:** Automated dependency updates
**Action:** Create new file

```yaml
version: 2
updates:
  # Python packages
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "03:00"
    open-pull-requests-limit: 5
    reviewers:
      - "vindon"
    labels:
      - "dependencies"
    commit-message:
      prefix: "chore(deps):"
      prefix-development: "chore(deps-dev):"
    allow:
      - dependency-type: "production"
    ignore:
      # Avoid major version bumps automatically; review manually
      - dependency-name: "langgraph"
        update-types:
          - "version-update:semver-major"
      - dependency-name: "langchain-core"
        update-types:
          - "version-update:semver-major"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "04:00"
    reviewers:
      - "vindon"
    labels:
      - "ci"
```

---

### 3.5 `.pre-commit-config.yaml`
**Purpose:** Local pre-commit hooks to catch issues before CI
**Action:** Create new file

```yaml
repos:
  # Ruff: linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
        exclude: ^tests/
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
      - id: mixed-line-ending
        args: ["--fix=lf"]

  # YAML formatting
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or:
          - yaml
          - markdown
        exclude: ^CHANGELOG\.md$

ci:
  autoupdate_schedule: weekly
  skip: []
```

---

### 3.6 `pipeline/metrics.py`
**Purpose:** Structured runtime health summary for observability
**Action:** Create new file

```python
"""
Runtime metrics and pipeline health summary helpers.

This module is intentionally lightweight and dependency-free so it can be used
from CLI entry points, tests, and future operational tooling without coupling to
LLM SDKs or the full pipeline runtime.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


@dataclass
class RunMetrics:
    """Represents a single pipeline run's operational health summary."""

    run_id: str
    started_at: str
    finished_at: str
    duration_seconds: float
    calls_total: int = 0
    calls_processed: int = 0
    quality_gate_failed: int = 0
    fallback_events: int = 0
    provider_failures: int = 0
    total_cost_usd: float = 0.0
    stages: dict[str, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["stages"] = payload.get("stages") or {}
        return payload


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def summarize_run(
    *,
    calls_total: int = 0,
    calls_processed: int = 0,
    quality_gate_failed: int = 0,
    fallback_events: int = 0,
    provider_failures: int = 0,
    total_cost_usd: float = 0.0,
    stages: Mapping[str, float] | None = None,
    run_id: str | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
    duration_seconds: float | None = None,
) -> RunMetrics:
    """Create a runtime health summary for a pipeline run."""

    started = started_at or _utc_now()
    finished = finished_at or _utc_now()
    if duration_seconds is None:
        try:
            started_dt = datetime.strptime(started, "%Y-%m-%dT%H:%M:%SZ")
            finished_dt = datetime.strptime(finished, "%Y-%m-%dT%H:%M:%SZ")
            duration_seconds = max((finished_dt - started_dt).total_seconds(), 0.0)
        except ValueError:
            duration_seconds = 0.0

    return RunMetrics(
        run_id=run_id or f"run-{started}",
        started_at=started,
        finished_at=finished,
        duration_seconds=float(duration_seconds),
        calls_total=int(calls_total),
        calls_processed=int(calls_processed),
        quality_gate_failed=int(quality_gate_failed),
        fallback_events=int(fallback_events),
        provider_failures=int(provider_failures),
        total_cost_usd=float(total_cost_usd),
        stages=dict(stages or {}),
    )


def write_run_summary(path: str | Path, metrics: RunMetrics | Mapping[str, Any]) -> Path:
    """Write a JSON summary to disk for operational inspection."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    payload = metrics.to_dict() if isinstance(metrics, RunMetrics) else dict(metrics)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return target
```

---

### 3.7 `docs/runbooks/README.md`
**Purpose:** Operational runbook index and onboarding
**Action:** Create new file

```md
# Operational Runbooks

This directory contains troubleshooting and recovery procedures for common pipeline scenarios.

## Quick reference

### Pipeline operation
- **[Pipeline Failure](./pipeline-failure.md)** — what to do when a batch job fails or stops mid-execution
- **[Provider Outage](./provider-outage.md)** — detecting and responding to LLM provider issues
- **[Quality Gate Failure](./quality-gate-failure.md)** — when extraction quality drops below threshold

### Before you run
1. Ensure all API keys are in `.env` or GitHub Secrets
2. Run `make check` locally to catch obvious issues
3. Check provider status before large batches

### After a failure
1. Review `outputs/pipeline.log` for the error
2. Check which stage failed
3. Look up the relevant runbook above
4. Do not re-run without understanding the root cause

## Observability

Run health summaries are written to `outputs/run_summary.json` after each batch.

Format:
```json
{
  "run_id": "run-2026-10-03T14:00:00Z",
  "started_at": "2026-10-03T14:00:00Z",
  "finished_at": "2026-10-03T14:15:30Z",
  "duration_seconds": 930.5,
  "calls_total": 100,
  "calls_processed": 92,
  "quality_gate_failed": 3,
  "fallback_events": 5,
  "provider_failures": 2,
  "total_cost_usd": 4.25,
  "stages": {
    "extraction": 450.2,
    "quality": 120.1,
    "insights": 360.2
  }
}
```

Use this for:
- tracking cost trends
- spotting provider issues early
- identifying stages that are slow or error-prone
- building a historical record of runs

## Contact

For questions or to add a runbook, open an issue or PR.
```

---

### 3.8 `docs/runbooks/pipeline-failure.md`
**Purpose:** Debugging when a batch job fails
**Action:** Create new file

```md
# Pipeline Failure Runbook

## Symptom

The pipeline stops mid-execution, or `run_batches.py` exits before export.

## Immediate checks

1. **Check the log**
   ```bash
   tail -50 outputs/pipeline.log
   ```
   Look for the last error and the stage name.

2. **Check the run summary**
   ```bash
   cat outputs/run_summary.json
   ```
   Confirm how many calls were processed and where it stopped.

3. **Determine the failure type**
   - Provider API error (timeout, 429, 503)?
   - Model output failed validation?
   - Quality gate rejected the batch?
   - Dataset/input issue?
   - Disk write or checkpoint error?

## Common causes

| Symptom | Cause | Action |
|---------|-------|--------|
| `APIError: Timeout` | Provider slow or unresponsive | Check provider status; reduce batch size |
| `ValidationError: missing field` | Model returned invalid JSON | Inspect `outputs/` for failed call logs |
| `QualityGateFailed: pass_rate=0.35 < 0.40` | Extraction quality below threshold | Review `qa_audit.json`; check input data |
| `OutOfMemory` or `Disk full` | Resource exhaustion | Split batch smaller; add disk space |
| `FileNotFoundError: dataset.csv` | Input file missing | Verify `LOCAL_CSV_PATH` in `pipeline/config.py` |

## Recovery steps

1. **Do not retry blindly.**
   - Review the root cause first
   - Retrying bad input data wastes money and time

2. **Check provider health**
   - Visit provider status pages (Anthropic, NVIDIA, Google)
   - Verify API keys in GitHub Secrets
   - Test with a small sample (1-5 calls) before full retry

3. **If the failure is code-related**
   - Fix the bug
   - Run a smoke test locally: `pytest tests/ -k "test_extraction" -v`
   - Commit and push
   - Re-run the batch

4. **If the failure is data-related**
   - Inspect the first few failed rows
   - Confirm transcript quality and format
   - Update `pipeline/config.py` validation thresholds if needed
   - Retry with a corrected dataset

5. **If the failure is a provider issue**
   - Wait for provider to recover (check status page)
   - Reduce batch size or RPM in `pipeline/config.py`
   - Retry with backoff

## Validation

Before re-running:
- [ ] Root cause is understood and logged
- [ ] No silent data loss between retries
- [ ] Logs clearly show the failure stage
- [ ] Provider health is confirmed (if applicable)
- [ ] A smoke test passes locally (if code changed)

## Owner review

All production pipeline failures should be reviewed by the engineering owner before rerun.
```

---

### 3.9 `docs/runbooks/provider-outage.md`
**Purpose:** Detecting and responding to LLM provider issues
**Action:** Create new file

```md
# Provider Outage Runbook

## Symptom

- Repeated timeouts or HTTP 503 errors
- Sudden spike in fallback behavior
- All calls to a specific model fail
- Rate-limit warnings (429 HTTP status)

## Immediate checks

1. **Check the log for provider errors**
   ```bash
   grep -i "nvidia\|anthropic\|gemini\|timeout\|429" outputs/pipeline.log | tail -20
   ```

2. **Confirm API key validity**
   ```bash
   # Check GitHub Secrets in repo settings
   # Verify key hasn't expired or been rotated
   ```

3. **Verify rate-limit status**
   - NVIDIA NIM: check account dashboard
   - Anthropic: check API key limits
   - Google Gemini: check free tier quota (500 RPD for 2.5-flash-lite)

4. **Test a single call manually**
   ```bash
   python -c "from pipeline.llm_clients import get_nvidia_client; c = get_nvidia_client(); print(c.models.list())"
   ```

## Common scenarios

| Provider | Symptom | Resolution |
|----------|---------|-----------|
| NVIDIA NIM | 503 Service Unavailable | Wait 5-10 min; reduce batch size; use Claude fallback |
| Anthropic Claude | 429 Rate Limited | Reduce `DEFAULT_RATE_LIMIT_RPM` in config.py; wait 60s |
| Google Gemini | 429 Quota Exceeded | Switch to gemini-2.0-flash-lite; wait 24h for quota reset |
| Any provider | Timeout (60s threshold) | Check network; increase `API_TIMEOUT_S`; retry smaller batches |

## Response actions

1. **Pause non-critical runs**
   - Stop any test or dev batches
   - Keep only critical production jobs

2. **Reduce load immediately**
   ```python
   # In pipeline/config.py, reduce one or both:
   DEFAULT_BATCH_SIZE = 10  # was 20
   DEFAULT_RATE_LIMIT_RPM = 10  # was 15
   ```

3. **Switch provider if available**
   - Insights: NVIDIA NIM → Claude fallback (automatic)
   - Extraction: Claude → Gemini fallback (automatic)
   - Check `pipeline/llm_clients.py` for fallback order

4. **Monitor recovery**
   ```bash
   # Run a 5-call test
   python run_batches.py --n-calls 5 --batch-size 5 -v
   ```

5. **Resume normal operation**
   - Revert batch size and rate limits
   - Re-run failed batch after 5-10 minutes

## Prevention

- Set up alerts on `outputs/run_summary.json`:
  - `provider_failures > 0` → check status
  - `fallback_events > calls_total * 0.1` → provider flaky
  - `duration_seconds` spike → timeout or slowness

- Add provider health check before production runs:
  ```bash
  python -m pipeline.circuit_breaker --check
  ```

## Owner review

Any provider outage affecting production should be:
- Logged in GitHub Issues
- Added to incident log
- Used to inform batch scheduling decisions

Contact provider support for extended outages.
```

---

### 3.10 `docs/runbooks/quality-gate-failure.md`
**Purpose:** Diagnosing quality drops
**Action:** Create new file

```md
# Quality Gate Failure Runbook

## Symptom

Pipeline halts with:
```
QualityGateFailed: pass_rate=0.35 < MIN_PASS_RATE=0.40
```

or

```
QUALITY_WARN: pass_rate=0.65 < QUALITY_WARN_RATE=0.70
```

## Immediate check

```bash
cat outputs/qa_audit.json | python -m json.tool | head -50
```

Look for:
- `pass_rate` (actual vs. threshold)
- `failed_reasons` (what kinds of failures)
- `high_grade_count` vs. `medium_grade_count` vs. `low_grade_count`

## Common causes

| Cause | Indicator | Action |
|-------|-----------|--------|
| Input data quality | High `MISSING_FIELDS` or `INVALID_FORMAT` | Review source CSV; improve transcript cleaning |
| Model underperformance | High `LOW_CONFIDENCE_SCORE` | Reduce batch size; test model locally |
| Threshold too strict | Borderline pass rate (35–45%) | Review `MIN_PASS_RATE` in config; may need adjustment |
| Provider fallback chain | High `FALLBACK_ATTEMPTED` | Check if primary provider is struggling |
| Extraction prompt issue | High `SCHEMA_VALIDATION_FAILED` | Inspect `prompts/system_prompt.txt`; test extraction |

## Recovery steps

1. **Inspect the audit report**
   ```bash
   python -c "
   import json
   with open('outputs/qa_audit.json') as f:
       audit = json.load(f)
   print(f'Pass rate: {audit[\"pass_rate\"]}')
   print(f'High: {audit[\"high_grade_count\"]}, Medium: {audit[\"medium_grade_count\"]}, Low: {audit[\"low_grade_count\"]}')
   for reason, count in audit['failed_reasons'].items():
       print(f'  {reason}: {count}')
   "
   ```

2. **Sample a few failed calls**
   ```bash
   ls -lrt outputs/call_* | tail -5  # find recent failures
   cat outputs/call_*.json | head -100  # inspect structure
   ```

3. **Determine root cause**
   - If input-related: fix data, retry
   - If model-related: test extraction locally
   - If threshold-related: adjust config and re-run

4. **Test a small batch before full retry**
   ```bash
   python run_batches.py --n-calls 10 --batch-size 5 -v
   ```

5. **Adjust thresholds or model if needed**
   ```python
   # In pipeline/config.py
   MIN_PASS_RATE = 0.35  # lower threshold if edge case
   INSIGHTS_TEMPERATURE = 0.2  # reduce temperature for stability
   ```

## Prevention

- Run a small smoke test before large batches
- Monitor `outputs/run_summary.json` for `quality_gate_failed` trend
- Keep audit logs for comparison across runs
- Set up alerts if pass rate drops >10% month-over-month

## Owner review

Quality gate failures should halt production to avoid shipping bad data downstream. Review each failure before continuing.
```

---

### 3.11 Update `.github/workflows/ci.yml`
**Purpose:** Add coverage gate, mypy, and safer pip setup
**Action:** Update existing file at line 44-54

Replace the Python setup section with:

```yaml
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Upgrade pip, setuptools, wheel
        run: python -m pip install --upgrade pip setuptools wheel

      - name: Install production dependencies
        run: pip install -r requirements.txt

      - name: Install dev dependencies
        run: pip install -r requirements-dev.txt
```

Add after line 63 (after `ruff check tests/`):

```yaml
      - name: Type check — mypy
        run: mypy pipeline/ --ignore-missing-imports
        continue-on-error: true  # Optional; set to false to enforce strict types
```

Replace line 105 (pytest command) with:

```yaml
      - name: Run unit tests with coverage gate
        run: |
          pytest tests/ -v --tb=short -m "not slow and not integration" \
            --cov=pipeline \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=80
```

---

### 3.12 `Makefile`
**Purpose:** Standard local commands for dev workflow
**Action:** Create new file

```makefile
.PHONY: help test lint format check clean install

PYTHON := python
SHELL := /bin/bash

help:
	@echo "Available commands:"
	@echo "  make install       Install development dependencies"
	@echo "  make lint          Run linting checks (ruff)"
	@echo "  make format        Auto-format code with ruff"
	@echo "  make type          Run mypy type checking (optional)"
	@echo "  make test          Run tests with coverage (min 80%)"
	@echo "  make check         Run all checks (lint + test)"
	@echo "  make clean         Remove build artifacts and caches"

install:
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	ruff check .

format:
	ruff format .

type:
	mypy pipeline/ --ignore-missing-imports

test:
	pytest tests/ -v --tb=short -m "not slow and not integration" \
		--cov=pipeline \
		--cov-report=term-missing \
		--cov-report=xml \
		--cov-fail-under=80

check: lint test
	@echo "✓ All checks passed"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
```

---

## Summary table

| File | Action | Impact |
|------|--------|--------|
| `.github/CODEOWNERS` | Create | Ownership clarity |
| `.github/SECURITY.md` | Create | Security policy |
| `CONTRIBUTING.md` | Create | Contributor onboarding |
| `.github/dependabot.yml` | Create | Automated dep updates |
| `.pre-commit-config.yaml` | Create | Local quality gates |
| `pipeline/metrics.py` | Create | Operational visibility |
| `docs/runbooks/README.md` | Create | Runbook index |
| `docs/runbooks/pipeline-failure.md` | Create | Failure diagnosis |
| `docs/runbooks/provider-outage.md` | Create | Outage response |
| `docs/runbooks/quality-gate-failure.md` | Create | Quality troubleshooting |
| `.github/workflows/ci.yml` | Update | Coverage gate, mypy, pip safety |
| `Makefile` | Create | Dev convenience |
| GitHub Settings → Branches | Configure | Branch protection |
| GitHub Settings → Security | Configure | Dependabot, scanning |

---

## Execution checklist

### For Claude Code (in order)

- [ ] Create `.github/CODEOWNERS`
- [ ] Create `.github/SECURITY.md`
- [ ] Create `CONTRIBUTING.md`
- [ ] Create `.github/dependabot.yml`
- [ ] Create `.pre-commit-config.yaml`
- [ ] Create `pipeline/metrics.py`
- [ ] Create `docs/runbooks/README.md`
- [ ] Create `docs/runbooks/pipeline-failure.md`
- [ ] Create `docs/runbooks/provider-outage.md`
- [ ] Create `docs/runbooks/quality-gate-failure.md`
- [ ] Update `.github/workflows/ci.yml`
- [ ] Create `Makefile`

### For GitHub UI (after code merged)

- [ ] Enable branch protection on `main`
- [ ] Require PR reviews (1 approval)
- [ ] Require passing status checks
- [ ] Enable Dependabot
- [ ] Enable secret scanning
- [ ] Verify API key secrets are stored

**Total time:** ~50 min (code + UI)

