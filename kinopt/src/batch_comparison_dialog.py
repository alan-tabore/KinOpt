"""Qt table for comparing completed batch optimization results."""

from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
)

from kinopt.src.optimization_comparison import (
    compare_fit,
    summarize_multistart_groups,
)
from kinopt.src.optimization_export import write_batch_csv, write_batch_json
from kinopt.src.optimization_queue import JobStatus


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
    description = " → ".join(method for method in methods if method) or "—"
    if config.exploratory_fraction is not None:
        return f"Two-stage {config.exploratory_fraction:.0%} → {description}"
    return description


def _comparison_rows(jobs):
    completed = [
        job
        for job in jobs
        if job.status is JobStatus.COMPLETED and job.result is not None
    ]
    measurements = []
    unavailable = []
    for job in completed:
        try:
            measurements.append((job, compare_fit(job.config, job.result.parameters)))
        except (TypeError, ValueError, FloatingPointError) as error:
            unavailable.append((job, str(error)))

    groups = defaultdict(list)
    for job, comparison in measurements:
        groups[comparison.dataset_fingerprint].append((job, comparison))

    rows = []
    ordered_groups = sorted(
        groups.values(),
        key=lambda group: min(item[0].position for item in group),
    )
    for dataset_number, group in enumerate(ordered_groups, start=1):
        for rank, (job, comparison) in enumerate(
            sorted(group, key=lambda item: (item[1].rmse, item[0].position)),
            start=1,
        ):
            rows.append((dataset_number, rank, job, comparison, ""))
    for job, message in unavailable:
        rows.append((None, None, job, None, message))
    return rows


class BatchComparisonDialog(QDialog):
    """Rank completed jobs using one solver-independent fit metric."""

    HEADERS = (
        "Data",
        "Rank",
        "Job",
        "Model",
        "Strategy",
        "Fit RMSE",
        "Validation RMSE",
        "Overall RMSE",
        "Solver cost",
        "Free parameters",
        "Evaluations",
        "Duration",
    )
    SUMMARY_HEADERS = (
        "Group",
        "Seed",
        "Completed",
        "Converged",
        "Best job",
        "Best RMSE",
        "Median RMSE",
        "Max relative range",
    )

    def __init__(self, jobs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compare completed optimizations")
        self.resize(1260, 430)

        explanation = QLabel(
            "Fit and validation RMSE are recalculated from each model prediction "
            "and the measured rates, independently of the selected solver cost. "
            "A validation score uses an experiment excluded from fitting. "
            "Jobs are ranked together only when their measured rate series match. "
            "For multi-start groups, a lower maximum relative parameter range "
            "means the fitted parameters agree more closely."
        )
        explanation.setWordWrap(True)

        self.table = QTableWidget(0, len(self.HEADERS), self)
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        widths = (60, 60, 190, 190, 135, 105, 120, 110, 110, 145, 110, 95)
        for column, width in enumerate(widths):
            self.table.setColumnWidth(column, width)

        self.summary_table = QTableWidget(0, len(self.SUMMARY_HEADERS), self)
        self.summary_table.setHorizontalHeaderLabels(self.SUMMARY_HEADERS)
        self.summary_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.summary_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.summary_table.verticalHeader().setVisible(False)
        summary_header = self.summary_table.horizontalHeader()
        summary_header.setSectionResizeMode(QHeaderView.Interactive)
        summary_header.setSectionResizeMode(0, QHeaderView.Stretch)
        for column, width in enumerate((180, 70, 105, 105, 230, 110, 120, 175)):
            self.summary_table.setColumnWidth(column, width)

        self.stability_table = QTableWidget(0, 7, self)
        self.stability_table.setHorizontalHeaderLabels(
            ("Group", "Parameter", "Minimum", "Median", "Maximum", "Relative range", "Unit")
        )
        self.stability_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stability_table.verticalHeader().setVisible(False)
        self.stability_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.table, "Completed runs")
        self.tabs.addTab(self.summary_table, "Multi-start groups")
        self.tabs.addTab(self.stability_table, "Parameter stability")

        self.export_json_button = QPushButton("Export JSON…")
        self.export_csv_button = QPushButton("Export CSV…")
        export_controls = QHBoxLayout()
        export_controls.addWidget(self.export_json_button)
        export_controls.addWidget(self.export_csv_button)
        export_controls.addStretch(1)
        self.export_json_button.clicked.connect(self.export_json)
        self.export_csv_button.clicked.connect(self.export_csv)

        self.note = QLabel()
        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(explanation)
        layout.addWidget(self.tabs)
        layout.addLayout(export_controls)
        layout.addWidget(self.note)
        layout.addWidget(close_buttons)
        self.set_jobs(jobs)

    def set_jobs(self, jobs):
        """Reload completed jobs so an open comparison stays current."""
        self.jobs = tuple(jobs)
        rows = _comparison_rows(self.jobs)
        self.table.setRowCount(len(rows))
        for row, (dataset, rank, job, comparison, error) in enumerate(rows):
            result = job.result
            values = (
                "—" if dataset is None else str(dataset),
                "—" if rank is None else str(rank),
                job.name,
                _model_description(job.config),
                _strategy_description(job.config),
                (
                    "Unavailable"
                    if comparison is None
                    else format(comparison.rmse, ".6g")
                ),
                (
                    "—"
                    if comparison is None or comparison.validation_rmse is None
                    else format(comparison.validation_rmse, ".6g")
                ),
                (
                    "Unavailable"
                    if comparison is None
                    else format(comparison.overall_rmse, ".6g")
                ),
                format(result.cost, ".6g"),
                str(len(result.parameters)),
                "—" if result.evaluations is None else str(result.evaluations),
                f"{result.elapsed_seconds:.2f} s",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(error or value)
                if column in {0, 1, 5, 6, 7, 8, 9, 10, 11}:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, column, item)
        summaries = summarize_multistart_groups(self.jobs)
        self.summary_table.setRowCount(len(summaries))
        for row, summary in enumerate(summaries):
            values = (
                summary.group_name,
                "—" if summary.seed is None else str(summary.seed),
                f"{summary.completed_count}/{summary.total_count}",
                f"{summary.converged_count}/{summary.completed_count}",
                summary.best_job_name or "—",
                (
                    "—"
                    if summary.best_rmse is None
                    else format(summary.best_rmse, ".6g")
                ),
                (
                    "—"
                    if summary.median_rmse is None
                    else format(summary.median_rmse, ".6g")
                ),
                (
                    "—"
                    if summary.maximum_relative_parameter_range is None
                    else format(
                        summary.maximum_relative_parameter_range,
                        ".2%",
                    )
                ),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(summary.message or value)
                if column in {1, 2, 3, 5, 6, 7}:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.summary_table.setItem(row, column, item)

        stability_rows = [
            (summary.group_name, parameter)
            for summary in summaries
            for parameter in summary.parameter_stability
        ]
        self.stability_table.setRowCount(len(stability_rows))
        for row, (group_name, parameter) in enumerate(stability_rows):
            values = (
                group_name,
                parameter.name,
                format(parameter.minimum, ".6g"),
                format(parameter.median, ".6g"),
                format(parameter.maximum, ".6g"),
                format(parameter.relative_range, ".2%"),
                parameter.unit or "—",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {2, 3, 4, 5}:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.stability_table.setItem(row, column, item)
        self.note.setText(
            f"{len(rows)} completed optimization(s) shown. "
            f"{len(summaries)} multi-start group(s). "
            "RMSE has the same unit as the measured reaction rate."
        )

    def export_json(self):
        """Ask for a destination and export complete queue configurations."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export optimization comparison as JSON",
            "kinopt-optimization-comparison.json",
            "JSON files (*.json)",
        )
        if path:
            self._write_export(write_batch_json, path, "JSON")

    def export_csv(self):
        """Ask for a destination and export a spreadsheet-friendly table."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export optimization comparison as CSV",
            "kinopt-optimization-comparison.csv",
            "CSV files (*.csv)",
        )
        if path:
            self._write_export(write_batch_csv, path, "CSV")

    def _write_export(self, writer, path, format_name):
        try:
            writer(path, self.jobs)
        except (OSError, TypeError, ValueError) as error:
            QMessageBox.critical(self, "Export comparison", str(error))
            return
        self.note.setText(f"Exported {format_name} comparison to {path}.")
