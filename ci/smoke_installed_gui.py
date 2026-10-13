"""Open and close each public launcher using the installed package, outside the checkout."""

from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import traceback

from PyQt5.QtCore import QTimer
from kinopt.src import main as gui


def check_launcher(mode):
    app = gui.QApplication.instance() or gui.QApplication([])
    observations = []
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / 'trial results'

        def inspect_window():
            try:
                windows = [widget for widget in app.topLevelWidgets()
                           if isinstance(widget, gui.MainWindow) and widget.isVisible()]
                assert len(windows) == 1, f'Expected one visible window, got {len(windows)}'
                assert windows[0].results_directory == output
                assert not output.exists(), 'Opening KinOpt must not create a result directory'
                observations.append(True)
                windows[0].close()
            except Exception:
                traceback.print_exc()
                app.exit(1)

        QTimer.singleShot(0, inspect_window)
        sys.argv = ['kinopt', '--results-dir', str(output)]
        try:
            if mode == 'console':
                runpy.run_path(shutil.which('kinopt'), run_name='__main__')
            elif mode == 'module':
                runpy.run_module('kinopt', run_name='__main__')
            elif mode == 'legacy':
                runpy.run_path(gui.__file__, run_name='__main__')
            else:
                raise ValueError(f'Unknown launcher: {mode}')
        except SystemExit as exit_status:
            assert exit_status.code == 0, exit_status.code
        assert observations == [True]
    print(f'{mode}: installed GUI opened and closed successfully ({gui.__file__})')


if __name__ == '__main__':
    check_launcher(sys.argv[1])
