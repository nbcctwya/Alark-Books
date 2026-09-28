#!/usr/bin/env python
"""Stable command entry point; run with the webproj Python environment."""
from alark_publishing.runtime import prepare

if __name__ == '__main__':
    prepare()
    from alark_publishing.cli import main
    raise SystemExit(main())
