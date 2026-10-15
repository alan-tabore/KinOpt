"""Qt smoke tests for the pre-run review dialog."""

from PyQt5.QtWidgets import QApplication, QDialog

from kinopt.src.optimization_review import build_optimization_review
from kinopt.src.optimization_review_dialog import OptimizationReviewDialog


def test_review_dialog_displays_summary_and_accepts_start(
    serializable_config,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv('QT_QPA_PLATFORM', 'offscreen')
    monkeypatch.setenv('MPLCONFIGDIR', str(tmp_path / 'matplotlib'))
    app = QApplication.instance() or QApplication([])
    review = build_optimization_review(
        serializable_config,
        dataset_names=('experiment.csv',),
    )
    dialog = OptimizationReviewDialog(review)
    try:
        text = dialog.summary.toPlainText()
        assert 'experiment.csv' in text
        assert 'Nth-order model' in text
        assert 'Nelder-Mead' in text
        assert 'A1' in text

        dialog.start_button.click()
        assert dialog.result() == QDialog.Accepted
    finally:
        dialog.close()
        dialog.deleteLater()
        app.processEvents()
