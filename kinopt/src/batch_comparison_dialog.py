"""Qt table for comparing completed batch optimization results."""

from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from kinopt.src.optimization_comparison import compare_fit
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
    return " → ".join(method for method in methods if method) or "—"


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
        "RMSE",
        "Solver cost",
        "Free parameters",
        "Evaluations",
        "Duration",
    )

    def __init__(self, jobs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compare completed optimizations")
        self.resize(1260, 430)

        explanation = QLabel(
            "RMSE is recalculated from each model prediction and the measured "
            "rates, independently of the selected solver cost. Lower is better. "
            "Jobs are ranked together only when their measured rate series match."
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
        widths = (60, 60, 190, 190, 135, 105, 110, 145, 110, 95)
        for column, width in enumerate(widths):
            self.table.setColumnWidth(column, width)

        self.note = QLabel()
        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(explanation)
        layout.addWidget(self.table)
        layout.addWidget(self.note)
        layout.addWidget(close_buttons)
        self.set_jobs(jobs)

    def set_jobs(self, jobs):
        """Reload completed jobs so an open comparison stays current."""
        rows = _comparison_rows(jobs)
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
                format(result.cost, ".6g"),
                str(len(result.parameters)),
                "—" if result.evaluations is None else str(result.evaluations),
                f"{result.elapsed_seconds:.2f} s",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(error or value)
                if column in {0, 1, 5, 6, 7, 8, 9}:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, column, item)
        self.note.setText(
            f"{len(rows)} completed optimization(s) shown. "
            "RMSE has the same unit as the measured reaction rate."
        )
