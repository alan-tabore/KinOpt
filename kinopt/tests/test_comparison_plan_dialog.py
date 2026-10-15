"""Exercise the optimization comparison-plan assistant."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog
import pytest

from kinopt.src.comparison_plan_dialog import ComparisonPlanDialog
from kinopt.src.optimization_queue import JobStatus, OptimizationQueue
from kinopt.src.optimization_runner import LOG_SPACE_LEAST_SQUARES


@pytest.fixture
def qt_app():
    return QApplication.instance() or QApplication([])


def test_default_plan_adds_models_and_methods_atomically(
    qt_app,
    tmp_path,
    serializable_config,
):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    dialog = ComparisonPlanDialog(queue, serializable_config)
    try:
        models, methods, profiles = dialog.selected_values()
        assert models == (
            'rate_for_nth_order',
            'rate_for_autocatalytic',
            'rate_for_kamal',
        )
        assert methods == (LOG_SPACE_LEAST_SQUARES, 'L-BFGS-B')
        assert len(profiles) == 1
        assert dialog.add_button.text() == 'Add 6 job(s)'

        dialog.add_jobs()

        assert dialog.result() == QDialog.Accepted
        jobs = queue.list_jobs()
        assert len(jobs) == 6
        assert all(job.status is JobStatus.PENDING for job in jobs)
        assert len({job.group_identifier for job in jobs}) == 1
        assert all(job.group_name == 'Model comparison' for job in jobs)
        assert all(job.group_kind == 'comparison_plan' for job in jobs)
        assert {job.config.rate_law.__name__ for job in jobs} == set(models)
        assert {job.config.local_method for job in jobs} == set(methods)
        assert all(
            np.array_equal(
                job.config.experimental_rate,
                serializable_config.experimental_rate,
            )
            for job in jobs
        )
    finally:
        dialog.close()
        dialog.deleteLater()
        qt_app.processEvents()


def test_plan_selection_preview_updates(qt_app, tmp_path, serializable_config):
    queue = OptimizationQueue(tmp_path / 'queue.sqlite3')
    dialog = ComparisonPlanDialog(queue, serializable_config)
    try:
        for index in range(1, dialog.rate_models.count()):
            dialog.rate_models.item(index).setCheckState(0)
        for index in range(dialog.local_methods.count()):
            dialog.local_methods.item(index).setCheckState(
                2 if index == 0 else 0
            )
        qt_app.processEvents()

        assert dialog.add_button.text() == 'Add 1 job(s)'
        assert '1 model(s) × 1 method(s) × 1 profile(s)' in (
            dialog.preview.text()
        )
    finally:
        dialog.close()
        dialog.deleteLater()
        qt_app.processEvents()
