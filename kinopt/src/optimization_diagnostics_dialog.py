"""Visual explanation of one completed optimization result."""

from html import escape

import numpy as np
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

from kinopt.src.optimization_comparison import diagnose_fit


def _solver_explanation(result):
    if result.solver_success is True:
        return (
            "<b>Solver status:</b> convergence reported. This only describes "
            "the numerical stopping condition; parameter plausibility still "
            "needs to be checked."
        )
    if result.solver_success is False:
        return (
            '<b style="color:#b33;">Solver status:</b> convergence was not '
            "reported. Inspect the curves, residuals, and stopping message "
            "before using the fitted parameters."
        )
    return (
        "<b>Solver status:</b> no convergence status was provided. Inspect "
        "the curves and residuals before using the fitted parameters."
    )


class OptimizationDiagnosticsDialog(QDialog):
    """Show measured rates, fitted rates, and residuals for one stored job."""

    def __init__(self, job, parent=None):
        super().__init__(parent)
        self.resize(980, 760)
        self.job = None
        self.diagnostics = None

        self.summary = QLabel()
        self.summary.setTextFormat(Qt.RichText)
        self.summary.setWordWrap(True)
        self.guidance = QLabel(
            "Residual = model rate − measured rate. Values above zero mean "
            "that the model predicts a rate that is too high. Look for long "
            "runs on one side of zero or isolated large errors; either pattern "
            "can indicate a model limitation, an experimental issue, or a "
            "region needing closer inspection."
        )
        self.guidance.setWordWrap(True)

        self.figure = Figure(figsize=(9, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(self.summary)
        layout.addWidget(self.guidance)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(close_buttons)

        self.set_job(job)

    def set_job(self, job):
        """Replace the displayed result and redraw its diagnostics."""
        if job.result is None:
            raise ValueError("The selected optimization has no stored result.")
        diagnostics = diagnose_fit(job.config, job.result.parameters)
        self.job = job
        self.diagnostics = diagnostics
        self.setWindowTitle(f"Result diagnostics — {job.name}")

        message = escape(job.result.solver_message or "No message provided.")
        self.summary.setText(
            f"<h3>{escape(job.name)}</h3>"
            f"<p>{_solver_explanation(job.result)}</p>"
            "<p>"
            f"<b>RMSE:</b> {diagnostics.rmse:.6g} s⁻¹ &nbsp; "
            f"<b>Mean absolute error:</b> "
            f"{diagnostics.mean_absolute_error:.6g} s⁻¹ &nbsp; "
            f"<b>Mean residual (bias):</b> "
            f"{diagnostics.mean_residual:.6g} s⁻¹ &nbsp; "
            f"<b>Largest absolute residual:</b> "
            f"{diagnostics.maximum_absolute_error:.6g} s⁻¹"
            "</p>"
            f"<p><b>Measurements:</b> {diagnostics.sample_count} &nbsp; "
            f"<b>Duration:</b> {job.result.elapsed_seconds:.2f} s</p>"
            f"<p><b>Solver message:</b> {message}</p>"
        )

        self.figure.clear()
        rate_axis, residual_axis = self.figure.subplots(2, 1, sharex=True)
        sample = np.arange(1, diagnostics.sample_count + 1)
        rate_axis.plot(
            sample,
            diagnostics.measured_rate,
            label="Measured rate",
            linewidth=1.4,
        )
        rate_axis.plot(
            sample,
            diagnostics.model_rate,
            label="Model rate",
            linewidth=1.4,
            linestyle="--",
        )
        rate_axis.set_ylabel("Rate (s⁻¹)")
        rate_axis.set_title("Measured and fitted rates")
        rate_axis.legend()
        rate_axis.grid(alpha=0.2)

        residual_axis.axhline(0., color="black", linewidth=1.)
        if diagnostics.rmse > 0:
            residual_axis.axhspan(
                -diagnostics.rmse,
                diagnostics.rmse,
                color="tab:blue",
                alpha=0.1,
                label="± RMSE",
            )
        residual_axis.scatter(
            sample,
            diagnostics.residuals,
            s=15,
            color="tab:red",
            label="Residual",
        )
        residual_axis.set_xlabel("Stored measurement index")
        residual_axis.set_ylabel("Residual (s⁻¹)")
        residual_axis.set_title("Residuals: model − measured")
        residual_axis.legend()
        residual_axis.grid(alpha=0.2)

        self.figure.tight_layout()
        self.canvas.draw_idle()
