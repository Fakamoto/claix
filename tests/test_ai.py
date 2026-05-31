import pytest

from claix.ai import Claix


class FakeRun:
    def __init__(self, status: str):
        self.id = "run_test"
        self.status = status


def test_wait_for_run_returns_completed_run():
    claix = Claix.__new__(Claix)
    run = FakeRun("queued")

    def update_run(current_run):
        current_run.status = "completed"
        return current_run

    claix.update_run = update_run

    result = claix.wait_for_run(run, timeout_seconds=1, poll_interval=0)

    assert result.status == "completed"


def test_wait_for_run_raises_on_failed_run():
    claix = Claix.__new__(Claix)
    run = FakeRun("failed")

    with pytest.raises(RuntimeError, match="finished with status: failed"):
        claix.wait_for_run(run, timeout_seconds=1, poll_interval=0)
