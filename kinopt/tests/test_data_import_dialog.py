"""Exercise guided data preview, mapping, and conversion."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog

from kinopt.src.data_import_dialog import DataImportDialog


def test_dialog_infers_named_columns_and_validates_converted_data(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "experiment.csv"
    path.write_text(
        "temperature;conversion;reaction_rate;time\n"
        "76.85;10;6;0\n"
        "86.85;20;6;0.0166666666666667\n"
        "96.85;30;6;0.0333333333333333\n"
    )
    dialog = DataImportDialog([path])
    try:
        dialog.delimiter_edit.setText(";")
        dialog.has_header.setChecked(True)
        dialog.refresh_preview()
        dialog.time_unit.setCurrentIndex(dialog.time_unit.findData("minutes"))
        dialog.temperature_unit.setCurrentIndex(
            dialog.temperature_unit.findData("celsius")
        )
        dialog.rate_unit.setCurrentIndex(
            dialog.rate_unit.findData("per_minute")
        )
        dialog.extent_unit.setCurrentIndex(
            dialog.extent_unit.findData("percent")
        )

        assert dialog.column_combos["time"].currentData() == 3
        assert dialog.column_combos["temperature"].currentData() == 0
        assert dialog.column_combos["rate"].currentData() == 2
        assert dialog.column_combos["extent"].currentData() == 1

        dialog.validate_and_accept()

        assert dialog.result() == QDialog.Accepted
        imported = np.column_stack(dialog.datasets[0])
        np.testing.assert_allclose(
            imported,
            np.array(
                [
                    [0.0, 350.0, 0.1, 0.1],
                    [1.0, 360.0, 0.1, 0.2],
                    [2.0, 370.0, 0.1, 0.3],
                ]
            ),
        )
    finally:
        dialog.close()
        dialog.deleteLater()
        app.processEvents()
