"""Exercise the first graphical controls for persistent batch runs."""

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox
import pytest
from scipy.optimize import OptimizeResult

from kinopt.src.batch_optimization_dialog import BatchOptimizationDialog
from kinopt.src.optimization_queue import JobStatus, OptimizationQueue
from kinopt.src.optimization_runner import OptimizationRunResult


@pytest.fixture
def qt_app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def batch_dialog(qt_app, tmp_path, serializable_config):
    queue = OptimizationQueue(tmp_path / "queue.sqlite3")
    dialog = BatchOptimizationDialog(queue, lambda: serializable_config)
    try:
        yield dialog, queue
    finally:
        if dialog.has_running_worker():
            dialog.worker.request_cancel()
            dialog.worker.wait(3000)
        dialog.close()
        dialog.deleteLater()
        qt_app.processEvents()


def test_dialog_adds_current_setup_and_describes_it(batch_dialog):
    dialog, queue = batch_dialog
    dialog.name_edit.setText("Nth-order baseline")

    dialog.add_current_setup()

    jobs = queue.list_jobs()
    assert len(jobs) == 1
    assert jobs[0].status is JobStatus.PENDING
    assert dialog.table.rowCount() == 1
    assert dialog.table.item(0, 0).text() == "Nth-order baseline"
    assert dialog.table.item(0, 1).text() == "rate_for_nth_order"
    assert dialog.table.item(0, 2).text() == "Nelder-Mead"
    assert dialog.table.item(0, 3).text() == "Pending"


def test_dialog_runs_all_pending_jobs_without_blocking(batch_dialog, qt_app):
    dialog, queue = batch_dialog
    dialog.add_current_setup()
    dialog.add_current_setup()

    dialog.start_pending_jobs()
    assert dialog.has_running_worker()

    deadline = time.monotonic() + 5
    while dialog.has_running_worker() and time.monotonic() < deadline:
        qt_app.processEvents()
        time.sleep(0.005)
    qt_app.processEvents()

    assert not dialog.has_running_worker()
    assert [job.status for job in queue.list_jobs()] == [
        JobStatus.COMPLETED,
        JobStatus.COMPLETED,
    ]
    assert dialog.table.item(0, 7).text() != "—"
    assert dialog.status_label.text() == "All pending jobs have been processed."
    assert dialog.start_button.isEnabled()


def test_dialog_cancels_and_retries_selected_pending_job(batch_dialog):
    dialog, queue = batch_dialog
    dialog.add_current_setup()
    identifier = queue.list_jobs()[0].identifier
    dialog.table.selectRow(0)

    dialog.cancel_selected_or_current_job()
    assert queue.get(identifier).status is JobStatus.CANCELLED

    dialog.table.selectRow(0)
    assert dialog.table.item(0, 0).data(Qt.UserRole) == identifier
    dialog.retry_selected_job()
    assert queue.get(identifier).status is JobStatus.PENDING


def test_dialog_recovers_a_job_left_running(batch_dialog):
    dialog, queue = batch_dialog
    dialog.add_current_setup()
    identifier = queue.list_jobs()[0].identifier
    queue.set_status(identifier, JobStatus.RUNNING)

    dialog.recover_stopped_jobs()

    assert queue.get(identifier).status is JobStatus.INTERRUPTED
    assert "Recovered 1" in dialog.status_label.text()


def test_dialog_duplicates_reorders_and_deletes_jobs(batch_dialog, monkeypatch):
    dialog, queue = batch_dialog
    dialog.name_edit.setText("First")
    dialog.add_current_setup()
    dialog.name_edit.setText("Second")
    dialog.add_current_setup()

    dialog.table.selectRow(0)
    dialog.duplicate_selected_job()
    duplicate = queue.list_jobs()[-1]
    assert duplicate.name == "First copy"

    dialog.move_selected_pending_job(-1)
    assert [job.name for job in queue.list_jobs()] == [
        "First",
        "First copy",
        "Second",
    ]

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: QMessageBox.Yes,
    )
    dialog.delete_selected_job()
    assert [job.name for job in queue.list_jobs()] == ["First", "Second"]


def test_dialog_compares_completed_jobs_by_common_rmse(batch_dialog, qt_app):
    dialog, queue = batch_dialog
    dialog.name_edit.setText("Less accurate")
    dialog.add_current_setup()
    dialog.name_edit.setText("Exact fit")
    dialog.add_current_setup()
    assert not dialog.compare_button.isEnabled()

    jobs = queue.list_jobs()
    outcomes = (
        OptimizationRunResult(
            OptimizeResult(
                x=np.array([8e7, 55000., 1.4]),
                fun=0.01,
                success=True,
                message="done",
                nfev=20,
            ),
            1.2,
        ),
        OptimizationRunResult(
            OptimizeResult(
                x=np.array([1e8, 60000., 1.5]),
                fun=100.,
                success=True,
                message="done",
                nfev=30,
            ),
            1.5,
        ),
    )
    for job, outcome in zip(jobs, outcomes):
        queue.set_status(job.identifier, JobStatus.RUNNING)
        queue.complete(job.identifier, outcome)

    dialog.refresh()
    assert dialog.compare_button.isEnabled()
    dialog.show_completed_comparison()
    qt_app.processEvents()

    comparison = dialog.comparison_dialog
    assert comparison.table.rowCount() == 2
    assert comparison.table.item(0, 1).text() == "1"
    assert comparison.table.item(0, 2).text() == "Exact fit"
    assert float(comparison.table.item(0, 5).text()) == pytest.approx(0.)
    assert comparison.table.item(1, 2).text() == "Less accurate"

    queue.record_completed(
        jobs[0].config,
        outcomes[1],
        name="Direct optimization",
    )
    dialog.refresh()

    assert comparison.table.rowCount() == 3
    assert {
        comparison.table.item(row, 2).text()
        for row in range(comparison.table.rowCount())
    } == {"Exact fit", "Less accurate", "Direct optimization"}


def test_dialog_opens_residual_diagnostics_for_a_completed_job(
    batch_dialog,
    qt_app,
):
    dialog, queue = batch_dialog
    dialog.name_edit.setText("Result to inspect")
    dialog.add_current_setup()
    job = queue.list_jobs()[0]
    queue.set_status(job.identifier, JobStatus.RUNNING)
    queue.complete(
        job.identifier,
        OptimizationRunResult(
            OptimizeResult(
                x=np.array([1e8, 60000., 1.5]),
                fun=0.,
                success=False,
                message="Iteration budget reached",
                nfev=10,
            ),
            0.25,
        ),
    )
    dialog.refresh()

    dialog.table.clearSelection()
    qt_app.processEvents()
    assert not dialog.inspect_button.isEnabled()
    dialog.table.selectRow(0)
    assert dialog.inspect_button.isEnabled()
    dialog.inspect_button.click()
    qt_app.processEvents()

    diagnostics_dialog = dialog.diagnostics_dialog
    assert diagnostics_dialog is not None
    assert diagnostics_dialog.job.name == "Result to inspect"
    assert diagnostics_dialog.diagnostics.sample_count == 3
    assert len(diagnostics_dialog.figure.axes) == 2
    summary = diagnostics_dialog.summary.text()
    assert "RMSE" in summary
    assert "convergence was not reported" in summary
    assert "Iteration budget reached" in summary
