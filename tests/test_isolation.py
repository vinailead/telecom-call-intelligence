"""
Guards that the test suite never writes to the project's real runtime state.

Before these existed, every full run appended fake `quota_events` to the real
outputs/agent_memory.json (via Orchestrator._update_memory on the global MEMORY)
and ~100KB of test noise to the real outputs/pipeline.log — the file the
runbooks tell an operator to read when diagnosing a failed batch.
"""

import logging
from pathlib import Path

from pipeline.config import MEMORY_PATH, OUTPUT_DIR


def _read_or_none(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


class TestRealRuntimeStateIsolated:
    def test_global_memory_is_not_backed_by_the_real_file(self):
        from pipeline.memory import MEMORY

        assert Path(MEMORY.path).resolve() != Path(MEMORY_PATH).resolve()

    def test_saving_global_memory_leaves_the_real_file_untouched(self):
        from pipeline.memory import MEMORY

        # Safety first: this test calls save(). Never do that unless isolation is
        # verifiably in force — an un-isolated save() on the (never-loaded) global
        # overwrites the real agent_memory.json with an empty structure.
        assert (
            Path(MEMORY.path).resolve() != Path(MEMORY_PATH).resolve()
        ), "agent memory is NOT isolated; refusing to save() to the real file"
        before = _read_or_none(MEMORY_PATH)
        MEMORY.record_quota_event("isolation-test-model", "isolation-test-provider")
        MEMORY.save()
        assert _read_or_none(MEMORY_PATH) == before

    def test_pipeline_log_does_not_write_to_the_real_log_file(self):
        from pipeline.logger import get_logger

        get_logger("isolation-check")  # make sure the handlers exist
        real_log = (OUTPUT_DIR / "pipeline.log").resolve()
        file_handlers = [
            h for h in logging.getLogger("pipeline").handlers if isinstance(h, logging.FileHandler)
        ]
        assert file_handlers, "expected the pipeline logger to have a file handler"
        assert all(Path(h.baseFilename).resolve() != real_log for h in file_handlers)
