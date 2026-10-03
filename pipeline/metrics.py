"""Read-only health summary over the run manifests ExportAgent already writes.

Deliberately derives from ``run_manifest_*.json`` rather than defining a second
run-summary file: two sources describing the same run would drift.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from pipeline.config import BUDGET_USD, MIN_PASS_RATE, OUTPUT_DIR, QUALITY_WARN_RATE


@dataclass(frozen=True)
class RunHealth:
    run_timestamp: str
    pipeline_version: str
    n_requested: int
    n_analyzed: int
    n_failed: int
    qa_verdict: str
    qa_avg_score: float | None
    data_quality_pass_rate_pct: float | None
    total_cost_usd: float
    insights_source: str
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def summarize_manifest(manifest: Mapping[str, Any]) -> RunHealth:
    dq = manifest.get("data_quality_pass_rate_pct")
    cost = float((manifest.get("token_usage") or {}).get("total_cost_usd") or 0.0)
    n_failed = int(manifest.get("n_failed") or 0)
    source = str(manifest.get("insights_source") or "unknown")

    flags: list[str] = []
    if dq is not None:
        if dq < MIN_PASS_RATE * 100:
            flags.append("data_quality_below_min")
        elif dq < QUALITY_WARN_RATE * 100:
            flags.append("data_quality_below_warn")
    if n_failed:
        flags.append("failed_calls")
    if source == "rule_based_fallback":
        flags.append("insights_rule_based_fallback")
    if cost > BUDGET_USD:
        flags.append("over_budget")

    return RunHealth(
        run_timestamp=str(manifest.get("run_timestamp", "")),
        pipeline_version=str(manifest.get("pipeline_version", "")),
        n_requested=int(manifest.get("n_requested") or 0),
        n_analyzed=int(manifest.get("n_analyzed") or 0),
        n_failed=n_failed,
        qa_verdict=str(manifest.get("qa_verdict", "")),
        qa_avg_score=manifest.get("qa_avg_score"),
        data_quality_pass_rate_pct=dq,
        total_cost_usd=cost,
        insights_source=source,
        flags=flags,
    )


def latest_manifest(output_dir: Path | None = None) -> dict[str, Any] | None:
    # Resolved at call time so tests (and config overrides) can redirect OUTPUT_DIR.
    directory = output_dir if output_dir is not None else OUTPUT_DIR
    candidates = sorted(directory.glob("run_manifest_*.json"))
    if not candidates:
        return None
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


def main() -> int:
    manifest = latest_manifest()
    if manifest is None:
        print(f"No run_manifest_*.json found in {OUTPUT_DIR}/")
        return 1
    print(json.dumps(summarize_manifest(manifest).to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
