"""Qt assistant for creating model, method, and profile comparison plans."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
)

from kinopt.src.model_metadata import (
    kinetic_model_metadata,
    kinetic_model_names,
)
from kinopt.src.optimization_plan import (
    COMPARISON_LOCAL_METHODS,
    comparison_method_display_name,
    generate_comparison_plan,
)
from kinopt.src.optimization_profiles import (
    BALANCED_PROFILE_NAME,
    optimization_profile_names,
)
from kinopt.src.optimization_runner import LOG_SPACE_LEAST_SQUARES
from kinopt.src.selection_guidance import selection_guidance_for


class ComparisonPlanDialog(QDialog):
    """Create one queued cross-product from the current data and settings."""

    def __init__(self, queue, base_config, parent=None):
        super().__init__(parent)
        self.queue = queue
        self.base_config = base_config
        self.created_jobs = ()
        self.setWindowTitle("Build an optimization comparison plan")
        self.resize(680, 620)

        explanation = QLabel(
            "Choose rate models, local methods, and calculation profiles. "
            "KinOpt adds every selected combination to the sequential queue "
            "using the current measured data, cost function, and optional "
            "vitrification setup. The current model keeps its entered start; "
            "other model starts and all bounds come from the documented "
            "illustrative metadata. Every generated setup is stored as an "
            "individual immutable queued configuration."
        )
        explanation.setWordWrap(True)

        self.name_edit = QLineEdit("Model comparison")
        self.rate_models = QListWidget()
        self.local_methods = QListWidget()
        self.profiles = QListWidget()

        for name in kinetic_model_names("rate"):
            metadata = kinetic_model_metadata("rate", name)
            self._add_checkable_item(
                self.rate_models,
                metadata.display_name,
                name,
                checked=True,
                tooltip=f"{metadata.summary} {metadata.advice}",
            )
        for method in COMPARISON_LOCAL_METHODS:
            guidance = selection_guidance_for("local_optimization", method)
            self._add_checkable_item(
                self.local_methods,
                comparison_method_display_name(method),
                method,
                checked=method in {LOG_SPACE_LEAST_SQUARES, "L-BFGS-B"},
                tooltip="" if guidance is None else guidance.tooltip,
            )
        for profile_name in optimization_profile_names():
            self._add_checkable_item(
                self.profiles,
                profile_name,
                profile_name,
                checked=profile_name == BALANCED_PROFILE_NAME,
            )

        form = QFormLayout()
        form.addRow("Group name:", self.name_edit)
        form.addRow("Rate models:", self.rate_models)
        form.addRow("Local methods:", self.local_methods)
        form.addRow("Profiles:", self.profiles)

        self.preview = QLabel()
        self.preview.setWordWrap(True)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.add_button = self.buttons.button(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.add_jobs)
        self.buttons.rejected.connect(self.reject)
        for widget in (self.rate_models, self.local_methods, self.profiles):
            widget.itemChanged.connect(self._update_preview)
        self.name_edit.textChanged.connect(self._update_preview)

        layout = QVBoxLayout(self)
        layout.addWidget(explanation)
        layout.addLayout(form)
        layout.addWidget(self.preview)
        layout.addWidget(self.buttons)
        self._update_preview()

    @staticmethod
    def _add_checkable_item(
        widget,
        label,
        value,
        *,
        checked,
        tooltip="",
    ):
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, value)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        if tooltip:
            item.setToolTip(tooltip)
        widget.addItem(item)

    @staticmethod
    def _checked_values(widget):
        return tuple(
            widget.item(index).data(Qt.UserRole)
            for index in range(widget.count())
            if widget.item(index).checkState() == Qt.Checked
        )

    def selected_values(self):
        """Return the three selections in their displayed order."""
        return (
            self._checked_values(self.rate_models),
            self._checked_values(self.local_methods),
            self._checked_values(self.profiles),
        )

    def _update_preview(self):
        models, methods, profiles = self.selected_values()
        job_count = len(models) * len(methods) * len(profiles)
        self.preview.setText(
            f"This plan will add {job_count} job(s): "
            f"{len(models)} model(s) × {len(methods)} method(s) × "
            f"{len(profiles)} profile(s)."
        )
        self.add_button.setText(f"Add {job_count} job(s)")
        self.add_button.setEnabled(0 < job_count <= 50)

    def add_jobs(self):
        """Generate and atomically persist the selected comparison plan."""
        models, methods, profiles = self.selected_values()
        group_name = self.name_edit.text().strip() or "Comparison plan"
        try:
            entries = generate_comparison_plan(
                self.base_config,
                models,
                methods,
                profiles,
                group_name,
            )
            self.created_jobs = tuple(self.queue.add_many(
                (entry.config for entry in entries),
                (entry.name for entry in entries),
                group_name=group_name,
                group_kind="comparison_plan",
            ))
        except Exception as error:
            QMessageBox.critical(self, "Optimization comparison plan", str(error))
            return
        self.accept()
