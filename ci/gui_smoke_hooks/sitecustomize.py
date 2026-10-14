"""CI-only startup hook, injected into launcher subprocesses via PYTHONPATH."""

import os
from pathlib import Path
import traceback

from PyQt5.QtCore import QTimer
from kinopt.src.main import QApplication, MainWindow


original_show = MainWindow.show


def show_and_check(window):
    original_show(window)

    def check():
        try:
            assert window.isVisible()
            output = Path(os.environ['KINOPT_SMOKE_OUTPUT'])
            assert window.results_directory == output.resolve()
            assert not output.exists(), 'Opening KinOpt must not create a result directory'
            Path(os.environ['KINOPT_SMOKE_MARKER']).write_text('visible')
            window.close()
        except Exception:
            traceback.print_exc()
            QApplication.instance().exit(1)

    QTimer.singleShot(100, check)


MainWindow.show = show_and_check
