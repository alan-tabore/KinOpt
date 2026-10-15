"""Guided preview, column mapping, and unit conversion for kinetic data."""

import os
import warnings

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from kinopt.src.data_extraction import (
    DataImportSettings,
    extract_configured_data_single_file,
    normalize_delimiter,
    preview_delimited_file,
)


_COLUMN_HINTS = {
    "time": ("time", "temps", "second", "minute"),
    "temperature": ("temperature", "temp", "kelvin", "celsius"),
    "rate": ("rate", "speed", "vitesse", "dadt", "reaction rate"),
    "extent": ("extent", "conversion", "alpha", "avancement"),
}


def _suggest_column(headers, role, fallback):
    hints = _COLUMN_HINTS[role]
    for index, header in enumerate(headers):
        normalized = header.strip().lower().replace("_", " ")
        if any(hint in normalized for hint in hints):
            return index
    return min(fallback, max(0, len(headers) - 1))


class DataImportDialog(QDialog):
    """Preview selected files and produce validated standardized datasets."""

    def __init__(self, file_paths, parent=None):
        super().__init__(parent)
        self.file_paths = tuple(os.fspath(path) for path in file_paths)
        if not self.file_paths:
            raise ValueError("Select at least one data file.")
        self.datasets = None
        self.warning_messages = ()
        self._settings = None

        self.setWindowTitle("Import kinetic data")
        self.resize(820, 590)

        explanation = QLabel(
            "Check the preview, identify the four kinetic columns, and state "
            "the units used in the files. The same layout is applied to every "
            "selected file; KinOpt converts the values to seconds, Kelvin, "
            "s⁻¹, and a 0–1 extent before validation."
        )
        explanation.setWordWrap(True)

        self.file_combo = QComboBox()
        for path in self.file_paths:
            self.file_combo.addItem(os.path.basename(path), path)
        self.delimiter_edit = QLineEdit(",")
        self.delimiter_edit.setMaximumWidth(80)
        self.delimiter_edit.setToolTip(
            "Enter one character, or use tab / \\t for a tab-separated file."
        )
        self.skip_lines = QSpinBox()
        self.skip_lines.setRange(0, 10_000)
        self.has_header = QCheckBox("First remaining row contains column names")

        source_form = QFormLayout()
        source_form.addRow("Previewed file:", self.file_combo)
        source_form.addRow("Delimiter:", self.delimiter_edit)
        source_form.addRow("Lines to skip before the header/data:", self.skip_lines)
        source_form.addRow("Header:", self.has_header)

        self.preview = QTableWidget(0, 0)
        self.preview.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview.verticalHeader().setVisible(True)

        self.column_combos = {
            role: QComboBox()
            for role in ("time", "temperature", "rate", "extent")
        }
        self.time_unit = self._unit_combo(
            (("Seconds", "seconds"), ("Minutes", "minutes"))
        )
        self.temperature_unit = self._unit_combo(
            (("Kelvin", "kelvin"), ("Degrees Celsius", "celsius"))
        )
        self.rate_unit = self._unit_combo(
            (("Per second (s⁻¹)", "per_second"), ("Per minute (min⁻¹)", "per_minute"))
        )
        self.extent_unit = self._unit_combo(
            (("Fraction from 0 to 1", "fraction"), ("Percent from 0 to 100", "percent"))
        )

        mapping_form = QFormLayout()
        mapping_form.addRow("Time column:", self._column_with_unit("time", self.time_unit))
        mapping_form.addRow(
            "Temperature column:",
            self._column_with_unit("temperature", self.temperature_unit),
        )
        mapping_form.addRow("Reaction-rate column:", self._column_with_unit("rate", self.rate_unit))
        mapping_form.addRow("Extent column:", self._column_with_unit("extent", self.extent_unit))

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.button(QDialogButtonBox.Ok).setText("Validate and import")

        layout = QVBoxLayout(self)
        layout.addWidget(explanation)
        layout.addLayout(source_form)
        layout.addWidget(QLabel("File preview:"))
        layout.addWidget(self.preview, 1)
        layout.addLayout(mapping_form)
        layout.addWidget(self.status_label)
        layout.addWidget(self.buttons)

        self.file_combo.currentIndexChanged.connect(self.refresh_preview)
        self.delimiter_edit.editingFinished.connect(self.refresh_preview)
        self.skip_lines.valueChanged.connect(self.refresh_preview)
        self.has_header.toggled.connect(self.refresh_preview)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        self.refresh_preview()

    @staticmethod
    def _unit_combo(options):
        combo = QComboBox()
        for label, value in options:
            combo.addItem(label, value)
        return combo

    def _column_with_unit(self, role, unit_combo):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.column_combos[role], 2)
        layout.addWidget(unit_combo, 1)
        return layout

    @property
    def settings(self):
        return self._settings or self._current_settings()

    def _current_settings(self):
        return DataImportSettings(
            delimiter=normalize_delimiter(self.delimiter_edit.text()),
            has_header=self.has_header.isChecked(),
            skip_lines=self.skip_lines.value(),
            columns=tuple(
                self.column_combos[role].currentData()
                for role in ("time", "temperature", "rate", "extent")
            ),
            time_unit=self.time_unit.currentData(),
            temperature_unit=self.temperature_unit.currentData(),
            rate_unit=self.rate_unit.currentData(),
            extent_unit=self.extent_unit.currentData(),
        )

    def refresh_preview(self):
        """Reload a small preview and refresh available column choices."""
        try:
            rows = preview_delimited_file(
                self.file_combo.currentData(),
                self.delimiter_edit.text(),
                self.skip_lines.value(),
            )
            width = max(len(row) for row in rows)
            if width < 4:
                raise ValueError(
                    "The preview has fewer than four columns. Check the delimiter."
                )
            padded = [row + ("",) * (width - len(row)) for row in rows]
            if self.has_header.isChecked():
                headers = padded[0]
                body = padded[1:]
            else:
                headers = tuple(f"Column {index + 1}" for index in range(width))
                body = padded

            self.preview.setColumnCount(width)
            self.preview.setHorizontalHeaderLabels(headers)
            self.preview.setRowCount(len(body))
            for row_index, row in enumerate(body):
                for column_index, value in enumerate(row):
                    self.preview.setItem(
                        row_index,
                        column_index,
                        QTableWidgetItem(value),
                    )
            self.preview.resizeColumnsToContents()

            for fallback, role in enumerate(
                ("time", "temperature", "rate", "extent")
            ):
                combo = self.column_combos[role]
                previous = combo.currentData()
                combo.blockSignals(True)
                combo.clear()
                for index, header in enumerate(headers):
                    combo.addItem(f"{index + 1}: {header}", index)
                suggested = (
                    previous
                    if isinstance(previous, int) and previous < width
                    else _suggest_column(headers, role, fallback)
                )
                combo.setCurrentIndex(int(suggested))
                combo.blockSignals(False)
            self.status_label.setText(
                f"Preview ready: {len(body)} data row(s) shown from "
                f"{os.path.basename(self.file_combo.currentData())}."
            )
            self.status_label.setStyleSheet("")
        except (OSError, ValueError) as error:
            self.preview.setRowCount(0)
            self.preview.setColumnCount(0)
            self.status_label.setText(str(error))
            self.status_label.setStyleSheet("color: #b00020;")

    def validate_and_accept(self):
        """Validate every file before exposing imported arrays to the caller."""
        try:
            settings = self._current_settings()
            datasets = []
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always", UserWarning)
                for path in self.file_paths:
                    datasets.append(
                        extract_configured_data_single_file(path, settings)
                    )
            self._settings = settings
            self.datasets = tuple(datasets)
            self.warning_messages = tuple(
                str(message.message) for message in captured
            )
        except (OSError, TypeError, ValueError) as error:
            self.status_label.setText(str(error))
            self.status_label.setStyleSheet("color: #b00020;")
            return
        self.accept()
