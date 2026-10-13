"""User-owned locations for files produced by KinOpt."""

from pathlib import Path


def results_directory(path=None):
    """Resolve an explicit directory or use Documents/KinOpt/results.

    No directory is created until a result is actually saved. Qt respects the
    desktop's configured Documents location, including on non-Linux systems.
    """
    if path is None:
        from PyQt5.QtCore import QStandardPaths

        documents = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        path = (Path(documents) if documents else Path.home() / 'Documents') / 'KinOpt' / 'results'
    return Path(path).expanduser().resolve()
