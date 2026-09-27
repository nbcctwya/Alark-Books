"""Run a local EPUBCheck release. Usage: python scripts/check_epub.py book.epub"""
from pathlib import Path
import argparse
import os
import subprocess
ROOT = Path(__file__).resolve().parents[1]

def validate(path, report=None):
    configured = os.environ.get('EPUBCHECK_JAR')
    matches = sorted((ROOT / '.cache/tools').glob('epubcheck-*/epubcheck.jar'))
    jar = Path(configured) if configured else matches[-1] if matches else None
    if not jar or not jar.is_file():
        raise FileNotFoundError('缺少 EPUBCheck。下载并解压到 .cache/tools，或设置 EPUBCHECK_JAR。详见 README.md。')
    command = ['java', '-jar', str(jar), str(path)]
    if report:
        command += ['--json', str(report)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    return result.returncode, (result.stdout + result.stderr).strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    code, message = validate(args.file, args.file.with_suffix('.epubcheck.json'))
    print(message)
    raise SystemExit(code)
