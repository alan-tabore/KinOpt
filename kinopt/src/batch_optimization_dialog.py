"""Qt interface for the persistent sequential optimization queue."""

from threading import Event

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from kinopt.src.batch_comparison_dialog import BatchComparisonDialog
from kinopt.src.optimization_diagnostics_dialog import (
    OptimizationDiagnosticsDialog,
)
from kinopt.src.optimization_queue import JobStatus
from kinopt.src.optimization_scheduler import SequentialOptimizationScheduler


class BatchOptimizationThread(QThread):
    """Run the persistent queue without blocking the Qt event loop."""

    job_finished = pyqtSignal(object)
    execution_error = pyqtSignal(str)

    def __init__(self, queue, parent=None):
        super().__init__(parent)
        self.queue = queue
        self._pause_requested = Event()

    def request_pause(self):
        """Finish the active job without claiming another one."""
        self._pause_requested.set()

    def request_cancel(self):
        """Cancel the active job and stop before the next one."""
        self._pause_requested.set()
        self.requestInterruption()

    def run(self):
        try:
            SequentialOptimizationScheduler(self.queue).run_pending(
                cancellation_requested=(
                    lambda job: self.isInterruptionRequested()
                ),
                should_continue=lambda: not self._pause_requested.is_set(),
                job_finished=self.job_finished.emit,
            )
        except Exception as error:
            self.execution_error.emit(f"{type(error).__name__}: {error}")


def _function_name(function):
    return "" if function is None else function.__name__


def _model_description(config):
    models = [
        _function_name(config.rate_law),
        _function_name(config.vitrification_law),
    ]
    return " + ".join(model for model in models if model) or "—"


def _strategy_description(config):
    methods = [config.global_method, config.local_method]
    return " → ".join(method for method in methods if method) or "—"


class BatchOptimizationDialog(QDialog):
    """Display, populate, and control one persistent optimization queue."""

    execution_started = pyqtSignal()
    execution_finished = pyqtSignal()

    HEADERS = (
        "Job",
        "Model",
        "Strategy",
        "State",
        "Solver",
        "Cost",
        "Duration",
        "Parameters",
        "Message",
    )

    def __init__(self, queue, config_provider, execution_allowed=None, parent=None):
        super().__init__(parent)
        self.queue = queue
        self.config_provider = config_provider
        self.execution_allowed = execution_allowed or (lambda: True)
        self.worker = None
        self.comparison_dialog = None
        self.diagnostics_dialog = None

        self.setWindowTitle("Batch optimizations")
        self.resize(1050, 480)

        explanation = QLabel(
            "Save several configurations, then run them one at a time. "
            "Changing the main form later does not modify queued jobs. "
            "Completed optimizations started from the main window are also "
            "added here automatically."
        )
        explanation.setWordWrap(True)

        self.table = QTableWidget(0, len(self.HEADERS), self)
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(len(self.HEADERS) - 1, QHeaderView.Stretch)
        for column, width in enumerate((150, 160, 110, 85, 105, 95, 80, 180)):
            self.table.setColumnWidth(column, width)

        self.add_button = QPushButton("Add current setup")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(
            "Optional name, for example: Kamal - wide bounds"
        )
        self.start_button = QPushButton("Start pending jobs")
        self.pause_button = QPushButton("Pause after current job")
        self.cancel_button = QPushButton("Cancel selected/current job")
        self.retry_button = QPushButton("Retry selected job")
        self.recover_button = QPushButton("Recover stopped jobs")
        self.refresh_button = QPushButton("Refresh")
        self.duplicate_button = QPushButton("Duplicate selected")
        self.move_up_button = QPushButton("Move pending job up")
        self.move_down_button = QPushButton("Move pending job down")
        self.delete_button = QPushButton("Delete selected")
        self.inspect_button = QPushButton("Inspect result")
        self.compare_button = QPushButton("Compare completed jobs")

        add_controls = QHBoxLayout()
        add_controls.addWidget(QLabel("New job name:"))
        add_controls.addWidget(self.name_edit, 1)
        add_controls.addWidget(self.add_button)

        execution_controls = QHBoxLayout()
        for button in (
            self.start_button,
            self.pause_button,
            self.cancel_button,
            self.retry_button,
            self.recover_button,
            self.refresh_button,
        ):
            execution_controls.addWidget(button)

        management_controls = QHBoxLayout()
        for button in (
            self.duplicate_button,
            self.move_up_button,
            self.move_down_button,
            self.delete_button,
        ):
            management_controls.addWidget(button)

        result_controls = QHBoxLayout()
        result_controls.addWidget(self.inspect_button)
        result_controls.addWidget(self.compare_button)
        result_controls.addStretch(1)

        self.status_label = QLabel("Ready.")
        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)

        layout = QVBoxLayout(self)
        layout.addWidget(explanation)
        layout.addWidget(self.table)
        layout.addLayout(add_controls)
        layout.addLayout(execution_controls)
        layout.addLayout(management_controls)
        layout.addLayout(result_controls)
        layout.addWidget(self.status_label)
        layout.addWidget(close_buttons)

        self.add_button.clicked.connect(self.add_current_setup)
        self.start_button.clicked.connect(self.start_pending_jobs)
        self.pause_button.clicked.connect(self.pause_after_current_job)
        self.cancel_button.clicked.connect(self.cancel_selected_or_current_job)
        self.retry_button.clicked.connect(self.retry_selected_job)
        self.recover_button.clicked.connect(self.recover_stopped_jobs)
        self.refresh_button.clicked.connect(self.refresh)
        self.duplicate_button.clicked.connect(self.duplicate_selected_job)
        self.move_up_button.clicked.connect(
            lambda: self.move_selected_pending_job(-1)
        )
        self.move_down_button.clicked.connect(
            lambda: self.move_selected_pending_job(1)
        )
        self.delete_button.clicked.connect(self.delete_selected_job)
        self.inspect_button.clicked.connect(self.show_selected_diagnostics)
        self.compare_button.clicked.connect(self.show_completed_comparison)
        self.table.itemSelectionChanged.connect(self._update_action_buttons)
        close_buttons.rejected.connect(self.close)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(500)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh()

    def has_running_worker(self):
        return self.worker is not None and self.worker.isRunning()

    def _selected_identifier(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        return self.table.item(selected_rows[0].row(), 0).data(Qt.UserRole)

    def _restore_selection(self, identifier):
        if identifier is None:
            return
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item.data(Qt.UserRole) == identifier:
                self.table.selectRow(row)
                return

    def _selected_job(self):
        identifier = self._selected_identifier()
        if identifier is None:
            return None
        try:
            return self.queue.get(identifier)
        except KeyError:
            return None

    def _update_action_buttons(self):
        job = self._selected_job()
        self.duplicate_button.setEnabled(job is not None)
        self.delete_button.setEnabled(
            job is not None and job.status is not JobStatus.RUNNING
        )
        self.inspect_button.setEnabled(
            job is not None
            and job.status is JobStatus.COMPLETED
            and job.result is not None
        )

        pending_jobs = [
            queued
            for queued in self.queue.list_jobs()
            if queued.status is JobStatus.PENDING
        ]
        pending_identifiers = [queued.identifier for queued in pending_jobs]
        if job is None or job.identifier not in pending_identifiers:
            self.move_up_button.setEnabled(False)
            self.move_down_button.setEnabled(False)
            return
        index = pending_identifiers.index(job.identifier)
        self.move_up_button.setEnabled(index > 0)
        self.move_down_button.setEnabled(index < len(pending_identifiers) - 1)

    @staticmethod
    def _solver_state(job):
        if job.result is None or job.result.solver_success is None:
            return "—"
        return "Converged" if job.result.solver_success else "Not converged"

    @staticmethod
    def _result_value(job, field, formatting):
        if job.result is None:
            return "—"
        return format(getattr(job.result, field), formatting)

    @staticmethod
    def _parameters(job):
        if job.result is None:
            return "—"
        return ", ".join(format(value, ".6g") for value in job.result.parameters)

    def refresh(self):
        """Reload the table from SQLite while preserving its selection."""
        selected_identifier = self._selected_identifier()
        jobs = self.queue.list_jobs()
        self.table.setRowCount(len(jobs))
        for row, job in enumerate(jobs):
            values = (
                job.name,
                _model_description(job.config),
                _strategy_description(job.config),
                job.status.value.capitalize(),
                self._solver_state(job),
                self._result_value(job, "cost", ".6g"),
                self._result_value(job, "elapsed_seconds", ".2f") + (
                    " s" if job.result is not None else ""
                ),
                self._parameters(job),
                job.message or "",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                if column == 0:
                    item.setData(Qt.UserRole, job.identifier)
                self.table.setItem(row, column, item)
        self._restore_selection(selected_identifier)
        self.pause_button.setEnabled(self.has_running_worker())
        self.start_button.setEnabled(not self.has_running_worker())
        self.recover_button.setEnabled(not self.has_running_worker())
        self.compare_button.setEnabled(
            sum(
                job.status is JobStatus.COMPLETED and job.result is not None
                for job in jobs
            )
            >= 2
        )
        if self.comparison_dialog is not None:
            self.comparison_dialog.set_jobs(jobs)
        self._update_action_buttons()

    def add_current_setup(self):
        """Snapshot the main form and append it to the queue."""
        config = self.config_provider()
        if config is None:
            return
        try:
            job = self.queue.add(config, name=self.name_edit.text())
        except Exception as error:
            QMessageBox.critical(self, "Batch optimization", str(error))
            return
        self.status_label.setText(f"Added {job.name}.")
        self.name_edit.clear()
        self.refresh()
        self._restore_selection(job.identifier)

    def start_pending_jobs(self):
        """Start one background worker for all currently pending jobs."""
        if self.has_running_worker():
            return
        if not self.execution_allowed():
            QMessageBox.information(
                self,
                "Batch optimization",
                "Another optimization is already running.",
            )
            return
        if not any(job.status is JobStatus.PENDING for job in self.queue.list_jobs()):
            self.status_label.setText("There are no pending jobs.")
            return

        self.worker = BatchOptimizationThread(self.queue, self)
        self.worker.job_finished.connect(self._job_finished)
        self.worker.execution_error.connect(self._execution_error)
        self.worker.finished.connect(self._worker_finished)
        self.status_label.setText("Running pending jobs one at a time…")
        self.execution_started.emit()
        self.refresh_timer.start()
        self.refresh()
        self.worker.start()

    def _job_finished(self, job):
        self.status_label.setText(
            f"{job.name}: {job.status.value}."
        )
        self.refresh()

    def _execution_error(self, message):
        self.status_label.setText(message)
        QMessageBox.critical(self, "Batch optimization", message)

    def _worker_finished(self):
        self.refresh_timer.stop()
        self.refresh()
        if any(
            job.status is JobStatus.PENDING
            for job in self.queue.list_jobs()
        ):
            self.status_label.setText("Batch paused. Pending jobs remain.")
        else:
            self.status_label.setText("All pending jobs have been processed.")
        self.execution_finished.emit()

    def pause_after_current_job(self):
        if self.has_running_worker():
            self.worker.request_pause()
            self.status_label.setText(
                "Pausing after the current optimization finishes…"
            )
            self.pause_button.setEnabled(False)

    def cancel_selected_or_current_job(self):
        identifier = self._selected_identifier()
        jobs = self.queue.list_jobs()
        selected = next(
            (job for job in jobs if job.identifier == identifier),
            None,
        )
        running = next(
            (job for job in jobs if job.status is JobStatus.RUNNING),
            None,
        )
        target = (
            selected
            if selected is not None
            and selected.status in {JobStatus.PENDING, JobStatus.RUNNING}
            else running
        )
        if target is None:
            self.status_label.setText("Select a pending job to cancel.")
            return
        try:
            if target.status is JobStatus.PENDING:
                self.queue.set_status(target.identifier, JobStatus.CANCELLED)
                self.status_label.setText(f"Cancelled {target.name}.")
            elif target.status is JobStatus.RUNNING and self.has_running_worker():
                self.worker.request_cancel()
                self.status_label.setText("Cancelling the current optimization…")
            else:
                self.status_label.setText(
                    "Only pending or currently running jobs can be cancelled."
                )
        except (RuntimeError, ValueError) as error:
            self.status_label.setText(str(error))
        self.refresh()

    def retry_selected_job(self):
        identifier = self._selected_identifier()
        if identifier is None:
            self.status_label.setText("Select a job to retry.")
            return
        job = self.queue.get(identifier)
        if job.status not in {
            JobStatus.FAILED,
            JobStatus.CANCELLED,
            JobStatus.INTERRUPTED,
        }:
            self.status_label.setText(
                "Only failed, cancelled, or interrupted jobs can be retried."
            )
            return
        retried = self.queue.set_status(identifier, JobStatus.PENDING)
        self.status_label.setText(f"Queued {retried.name} again.")
        self.refresh()
        self._restore_selection(identifier)

    def duplicate_selected_job(self):
        job = self._selected_job()
        if job is None:
            self.status_label.setText("Select a job to duplicate.")
            return
        try:
            duplicate = self.queue.duplicate(job.identifier)
        except (KeyError, TypeError, ValueError) as error:
            self.status_label.setText(str(error))
            self.refresh()
            return
        self.status_label.setText(f"Added {duplicate.name}.")
        self.refresh()
        self._restore_selection(duplicate.identifier)

    def move_selected_pending_job(self, direction):
        job = self._selected_job()
        if job is None:
            self.status_label.setText("Select a pending job to move.")
            return
        original_position = job.position
        try:
            moved = self.queue.move_pending(job.identifier, direction)
        except (KeyError, RuntimeError, ValueError) as error:
            self.status_label.setText(str(error))
            self.refresh()
            return
        if moved.position == original_position:
            self.status_label.setText(
                "The job is already at the end of the pending queue."
                if direction > 0
                else "The job is already at the start of the pending queue."
            )
        else:
            self.status_label.setText(f"Moved {moved.name}.")
        self.refresh()
        self._restore_selection(moved.identifier)

    def delete_selected_job(self):
        job = self._selected_job()
        if job is None:
            self.status_label.setText("Select a job to delete.")
            return
        if job.status is JobStatus.RUNNING:
            self.status_label.setText("A running job cannot be deleted.")
            return
        answer = QMessageBox.question(
            self,
            "Delete batch job",
            f"Delete {job.name} and its stored result?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self.queue.delete(job.identifier)
        except (KeyError, ValueError) as error:
            self.status_label.setText(str(error))
            self.refresh()
            return
        self.status_label.setText(f"Deleted {job.name}.")
        self.refresh()

    def recover_stopped_jobs(self):
        """Mark jobs left running by a stopped application as interrupted."""
        if self.has_running_worker():
            self.status_label.setText(
                "The active batch must finish before recovery."
            )
            return
        count = self.queue.recover_interrupted_jobs()
        if count:
            self.status_label.setText(
                f"Recovered {count} interrupted job(s); select one to retry."
            )
        else:
            self.status_label.setText("There are no stopped jobs to recover.")
        self.refresh()

    def show_completed_comparison(self):
        """Open a ranking of completed jobs using their common fit RMSE."""
        completed_jobs = [
            job
            for job in self.queue.list_jobs()
            if job.status is JobStatus.COMPLETED and job.result is not None
        ]
        if len(completed_jobs) < 2:
            self.status_label.setText(
                "Complete at least two jobs before comparing results."
            )
            return
        if self.comparison_dialog is not None:
            self.comparison_dialog.show()
            self.comparison_dialog.raise_()
            self.comparison_dialog.activateWindow()
            return
        self.comparison_dialog = BatchComparisonDialog(completed_jobs, self)
        self.comparison_dialog.setAttribute(Qt.WA_DeleteOnClose)
        self.comparison_dialog.destroyed.connect(
            lambda: setattr(self, "comparison_dialog", None)
        )
        self.comparison_dialog.show()

    def show_selected_diagnostics(self):
        """Open measured, fitted, and residual plots for a completed job."""
        job = self._selected_job()
        if (
            job is None
            or job.status is not JobStatus.COMPLETED
            or job.result is None
        ):
            self.status_label.setText(
                "Select a completed optimization to inspect its result."
            )
            return
        try:
            if self.diagnostics_dialog is None:
                self.diagnostics_dialog = OptimizationDiagnosticsDialog(
                    job,
                    self,
                )
                self.diagnostics_dialog.setAttribute(Qt.WA_DeleteOnClose)
                self.diagnostics_dialog.destroyed.connect(
                    lambda: setattr(self, "diagnostics_dialog", None)
                )
            else:
                self.diagnostics_dialog.set_job(job)
        except (TypeError, ValueError, FloatingPointError) as error:
            self.status_label.setText(
                f"Result diagnostics are unavailable: {error}"
            )
            return
        self.diagnostics_dialog.show()
        self.diagnostics_dialog.raise_()
        self.diagnostics_dialog.activateWindow()

    def closeEvent(self, event):
        if self.has_running_worker():
            QMessageBox.warning(
                self,
                "Batch optimization running",
                "Pause or cancel the batch before closing this window.",
            )
            event.ignore()
            return
        super().closeEvent(event)
