"""Tests for pipeline/metrics.py — pure functions over manifest dicts; filesystem redirected to tmp_path."""

import json

from pipeline import metrics
from pipeline.config import BUDGET_USD


def _manifest(**over):
    base = {
        "run_timestamp": "2026-10-03T10:00:00",
        "pipeline_version": "4.6.0",
        "n_requested": 20,
        "n_analyzed": 20,
        "n_failed": 0,
        "qa_verdict": "PASS",
        "qa_avg_score": 98.0,
        "data_quality_pass_rate_pct": 95.0,
        "insights_source": "llm_deliberated",
        "token_usage": {"total_cost_usd": 0.5},
    }
    return {**base, **over}


class TestSummarizeManifest:
    def test_healthy_run_has_no_flags(self):
        health = metrics.summarize_manifest(_manifest())
        assert health.flags == []
        assert health.total_cost_usd == 0.5

    def test_data_quality_between_min_and_warn_flags_warn_only(self):
        health = metrics.summarize_manifest(_manifest(data_quality_pass_rate_pct=55.0))
        assert health.flags == ["data_quality_below_warn"]

    def test_data_quality_below_min_flags_min_not_warn(self):
        health = metrics.summarize_manifest(_manifest(data_quality_pass_rate_pct=15.0))
        assert health.flags == ["data_quality_below_min"]

    def test_missing_data_quality_rate_is_not_flagged(self):
        health = metrics.summarize_manifest(_manifest(data_quality_pass_rate_pct=None))
        assert "data_quality_below_min" not in health.flags
        assert "data_quality_below_warn" not in health.flags

    def test_failed_calls_fallback_and_budget_flags(self):
        health = metrics.summarize_manifest(
            _manifest(
                n_failed=2,
                insights_source="rule_based_fallback",
                token_usage={"total_cost_usd": BUDGET_USD + 1},
            )
        )
        assert set(health.flags) == {"failed_calls", "insights_rule_based_fallback", "over_budget"}

    def test_tolerates_missing_fields(self):
        health = metrics.summarize_manifest({})
        assert health.n_requested == 0
        assert health.insights_source == "unknown"
        assert health.total_cost_usd == 0.0


class TestLatestManifest:
    def test_returns_none_when_no_manifests(self, tmp_path):
        assert metrics.latest_manifest(tmp_path) is None

    def test_picks_newest_by_filename(self, tmp_path):
        (tmp_path / "run_manifest_20260101_000000.json").write_text(json.dumps({"n_requested": 1}))
        (tmp_path / "run_manifest_20260202_000000.json").write_text(json.dumps({"n_requested": 2}))
        assert metrics.latest_manifest(tmp_path) == {"n_requested": 2}
