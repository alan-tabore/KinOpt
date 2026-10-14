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


def optimization_queue_path(path=None):
    """Resolve the SQLite file used to persist batch optimizations."""
    if path is None:
        from PyQt5.QtCore import QStandardPaths

        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        directory = Path(app_data) if app_data else Path.home() / '.kinopt'
        path = directory / 'optimization_queue.sqlite3'
    return Path(path).expanduser().resolve()
