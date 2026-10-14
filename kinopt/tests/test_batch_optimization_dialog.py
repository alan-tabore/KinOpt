"""Exercise the first graphical controls for persistent batch runs."""

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import pytest

from kinopt.src.batch_optimization_dialog import BatchOptimizationDialog
from kinopt.src.optimization_queue import JobStatus, OptimizationQueue


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
