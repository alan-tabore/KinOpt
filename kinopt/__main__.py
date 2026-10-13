"""Allow ``python -m kinopt`` to open the graphical application."""

from kinopt.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
