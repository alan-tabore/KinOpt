"""Terminal entry point for the graphical application."""

import argparse
from importlib.metadata import PackageNotFoundError, version
import os
from pathlib import Path
import sys


def main(argv=None):
    """Parse launcher options and open KinOpt's graphical interface."""
    parser = argparse.ArgumentParser(prog='kinopt', description='Open the KinOpt graphical interface.')
    try:
        installed_version = version('kinopt')
    except PackageNotFoundError:
        installed_version = 'source checkout'
    parser.add_argument('--version', action='version', version=f'KinOpt {installed_version}')
    parser.add_argument(
        '--results-dir', type=Path, metavar='DIRECTORY',
        help='save results in this directory (default: KinOpt/results in your Documents folder)',
    )
    args = parser.parse_args(argv)

    if (sys.platform.startswith('linux')
            and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY')
            and os.environ.get('QT_QPA_PLATFORM') not in ('offscreen', 'minimal')):
        parser.exit(1, 'KinOpt needs a graphical desktop. Run kinopt from a terminal in your desktop session.\n')

    # Help and version must work without importing Qt or requiring a display.
    from kinopt.src.main import QApplication, MainWindow

    app = QApplication.instance() or QApplication([parser.prog])
    app.setApplicationName('KinOpt')
    window = MainWindow(results_directory=args.results_dir)
    window.show()
    return app.exec_()
