"""
Tests for pipeline/agents/aggregation_agent.py — AggregationAgent.
Pure computation over extraction results; no mocks needed.
"""

import pytest

from pipeline.agents.aggregation_agent import AggregationAgent


class TestAggregationAgent:
    def test_outputs_metrics_and_token_usage(self, make_record):
        state = {
            "analysis_results": [make_record(call_id="c1"), make_record(call_id="c2")],
            "qa_passed_results": [make_record(call_id="c1"), make_record(call_id="c2")],
        }
        out = AggregationAgent().run(state)
        assert out["aggregated_metrics"]["kpis"]["total_calls_analyzed"] == 2
        assert out["token_usage"]["total_tokens"] == 2 * 3500

    def test_prefers_qa_passed_subset(self, make_record):
        state = {
            "analysis_results": [make_record(call_id=f"c{i}") for i in range(3)],
            "qa_passed_results": [make_record(call_id="c0")],
        }
        out = AggregationAgent().run(state)
        assert out["aggregated_metrics"]["kpis"]["total_calls_analyzed"] == 1
        scope = [d for d in out["decision_log"] if d["decision_type"] == "aggregation_scope"]
        assert scope[0]["evidence"]["qa_filtered"] is True

    def test_falls_back_to_full_results_when_qa_skipped(self, make_record):
        state = {
            "analysis_results": [make_record(call_id=f"c{i}") for i in range(3)],
            "qa_passed_results": [],
        }
        out = AggregationAgent().run(state)
        assert out["aggregated_metrics"]["kpis"]["total_calls_analyzed"] == 3
        scope = [d for d in out["decision_log"] if d["decision_type"] == "aggregation_scope"]
        assert scope[0]["evidence"]["qa_filtered"] is False

    def test_no_results_raises(self, make_record):
        with pytest.raises(RuntimeError, match="No results"):
            AggregationAgent().run({"analysis_results": [], "qa_passed_results": []})

        # Audit F1: when QualityAgent ran and rejected every record
        # (qa_passed_results == []), AggregationAgent must NOT fall back to
        # aggregating the rejected analysis_results.
        rejected = [make_record(call_id="c1", _qa_grade="LOW", _dq_gate_passed=False)]
        with pytest.raises(RuntimeError, match="No results"):
            AggregationAgent().run(
                {
                    "analysis_results": rejected,
                    "qa_passed_results": [],
                    "qa_report": {"dataset_verdict": "FAIL"},
                }
            )

    def test_cost_model_decision_logged(self, make_record):
        out = AggregationAgent().run({"analysis_results": [make_record()]})
        cost_decisions = [
            d for d in out["decision_log"] if d["decision_type"] == "cost_model_applied"
        ]
        assert len(cost_decisions) == 1
