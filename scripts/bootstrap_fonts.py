"""Download OFL fonts; instantiate static fonts for consistent PDF/EPUB rendering."""
from pathlib import Path
from urllib.request import urlopen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'design/fonts'
FONTS = {
    'Serif': ('notoserifsc', 'NotoSerifSC%5Bwght%5D.ttf'),
    'Sans': ('notosanssc', 'NotoSansSC%5Bwght%5D.ttf'),
}

if __name__ == '__main__':
    DEST.mkdir(parents=True, exist_ok=True)
    for kind, (folder, filename) in FONTS.items():
        target = DEST / f'Noto{kind}SC-Regular.ttf'
        if target.exists():
            print(f'Already installed: {target.name}')
            continue
        base = f'https://raw.githubusercontent.com/google/fonts/main/ofl/{folder}/'
        source = DEST / f'.{kind}-variable.ttf'
        with urlopen(base + filename, timeout=120) as response:
            source.write_bytes(response.read())
        with urlopen(base + 'OFL.txt', timeout=30) as response:
            (DEST / f'OFL-{kind}.txt').write_bytes(response.read())
        font = instantiateVariableFont(TTFont(source), {'wght': 400}, inplace=True)
        font.save(target)
        source.unlink()
        print(f'Installed: {target.name}')
