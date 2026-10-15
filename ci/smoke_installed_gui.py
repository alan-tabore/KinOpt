"""Open and close each public launcher using the installed package, outside the checkout."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
import tempfile

from kinopt.src import main as gui
from kinopt.examples import included_example_files


def check_launcher(mode):
    executable = Path(sysconfig.get_path('scripts')) / ('kinopt.exe' if os.name == 'nt' else 'kinopt')
    commands = {
        'console': [str(executable)],
        'module': [sys.executable, '-m', 'kinopt'],
        'legacy': [sys.executable, gui.__file__],
    }
    assert mode in commands, f'Unknown launcher: {mode}'
    source_package = Path(__file__).resolve().parents[1] / 'kinopt'
    assert Path(gui.__file__).resolve().parent.parent != source_package, 'Test the installed package'
    example_files = included_example_files()
    assert len(example_files) == 4
    assert all(path.is_file() for path in example_files)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / 'trial results'
        marker = root / 'window-checked.txt'
        hooks = root / 'test hooks'
        hooks.mkdir()
        shutil.copyfile(Path(__file__).parent / 'gui_smoke_hooks' / 'sitecustomize.py', hooks / 'sitecustomize.py')
        env = os.environ.copy()
        env.update(PYTHONPATH=str(hooks), KINOPT_SMOKE_OUTPUT=str(output), KINOPT_SMOKE_MARKER=str(marker))
        # Execute the real script or Windows .exe. The child-only hook closes
        # the window after inspection, without adding test options to KinOpt.
        result = subprocess.run(commands[mode] + ['--results-dir', str(output)], cwd=root,
                                env=env, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr
        assert marker.is_file(), 'The launcher exited without displaying and checking its window'
        assert marker.read_text() == 'visible'
    print(f'{mode}: installed GUI opened and closed successfully ({gui.__file__})')


if __name__ == '__main__':
    check_launcher(sys.argv[1])
