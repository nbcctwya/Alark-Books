"""Make Conda's native text libraries visible before importing WeasyPrint."""
import os
import sys
from pathlib import Path
from .paths import ROOT

def prepare():
    lib = Path(sys.prefix) / 'lib'
    if sys.platform.startswith('linux') and (lib / 'libpango-1.0.so.0').exists() and str(lib) not in os.environ.get('LD_LIBRARY_PATH', '').split(':'):
        env = dict(os.environ)
        env['LD_LIBRARY_PATH'] = str(lib) + ':' + env.get('LD_LIBRARY_PATH', '')
        os.execve(sys.executable, [sys.executable, *sys.argv], env)
    os.environ.setdefault('XDG_CACHE_HOME', str(ROOT / '.cache'))
