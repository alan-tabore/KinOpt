"""Qt dialog for reviewing an optimization before a long calculation."""

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from kinopt.src.optimization_review import review_to_html


class OptimizationReviewDialog(QDialog):
    """Show the exact frozen run configuration and allow it to be started."""

    def __init__(self, review, parent=None):
        super().__init__(parent)
        self.review = review
        self.setWindowTitle('Review optimization setup')
        self.resize(780, 700)

        introduction = QLabel(
            'This summary is built from the frozen configuration that will be '
            'sent to the optimizer. Return to the form if a value or warning '
            'needs attention.'
        )
        introduction.setWordWrap(True)

        self.summary = QTextBrowser(self)
        self.summary.setObjectName('optimization_review_summary')
        self.summary.setAccessibleName('Optimization setup summary')
        self.summary.setOpenExternalLinks(False)
        self.summary.setHtml(review_to_html(review))

        buttons = QDialogButtonBox(self)
        self.back_button = QPushButton('Back to editing', self)
        self.start_button = QPushButton('Start optimization', self)
        self.start_button.setDefault(True)
        buttons.addButton(self.back_button, QDialogButtonBox.RejectRole)
        buttons.addButton(self.start_button, QDialogButtonBox.AcceptRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(introduction)
        layout.addWidget(self.summary, 1)
        layout.addWidget(buttons)
