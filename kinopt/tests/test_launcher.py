"""Launcher behaviour: help without Qt, desktop checks and user output paths."""

import os
from pathlib import Path
import subprocess
import sys

import pytest

from kinopt.paths import results_directory


@pytest.mark.parametrize('argument,expected', [('--help', '--results-dir'), ('--version', 'KinOpt')])
def test_launcher_information_without_site_packages_or_display(argument, expected):
    env = os.environ.copy()
    for key in ('DISPLAY', 'WAYLAND_DISPLAY', 'QT_QPA_PLATFORM'):
        env.pop(key, None)
    completed = subprocess.run(
        [sys.executable, '-S', '-m', 'kinopt', argument],
        cwd=Path(__file__).resolve().parents[2], env=env, capture_output=True, text=True, timeout=15,
    )
    assert completed.returncode == 0, completed.stderr
    assert expected in completed.stdout


def test_launcher_without_desktop_gives_readable_error(monkeypatch, capsys):
    from kinopt import cli

    monkeypatch.setattr(cli.sys, 'platform', 'linux')
    for key in ('DISPLAY', 'WAYLAND_DISPLAY', 'QT_QPA_PLATFORM'):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(SystemExit) as error:
        cli.main([])
    assert error.value.code == 1
    assert 'graphical desktop' in capsys.readouterr().err


def test_result_directory_resolves_relative_path_without_creating_it(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    path = results_directory('my results')
    assert path == tmp_path / 'my results'
    assert not path.exists()


def test_default_result_directory_uses_desktop_documents(monkeypatch, tmp_path):
    from PyQt5.QtCore import QStandardPaths

    documents = tmp_path / 'Mes documents'
    monkeypatch.setattr(QStandardPaths, 'writableLocation', lambda location: str(documents))
    assert results_directory() == documents / 'KinOpt' / 'results'
    assert not documents.exists()
