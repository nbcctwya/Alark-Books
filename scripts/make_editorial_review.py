"""Render actual editorial PDF spreads and a chapter-opening comparison."""
from pathlib import Path
import pymupdf
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports/visual-review'

def spread(source, indices, target):
    with pymupdf.open(source) as doc:
        pages=[]
        for index in indices:
            pix=doc[index].get_pixmap(matrix=pymupdf.Matrix(1.7,1.7),alpha=False)
            pages.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    canvas=Image.new('RGB',(sum(p.width for p in pages)+60,max(p.height for p in pages)+40),'#e8e5df')
    x=20
    for page in pages:
        canvas.paste(page,(x,20))
        x+=page.width+20
    canvas.save(target)

def main():
    OUT.mkdir(exist_ok=True)
    folder=ROOT/'exports/layout-lab'
    def chapter_page(source, title):
        with pymupdf.open(source) as doc:
            return next(page for _,label,page in doc.get_toc() if label==title)
    def facing(page):
        left=page if page%2==0 else page+1
        return [left-1,left]
    portrait=folder/'layout-lab-portrait.pdf'
    landscape=folder/'layout-lab-landscape.pdf'
    first=chapter_page(portrait,'先有观察，再有表达')
    second=chapter_page(portrait,'搭建内容工作系统')
    spread(portrait,facing(first),OUT/'editorial-opening-spread.png')
    spread(portrait,facing(second),OUT/'editorial-method-spread.png')
    spread(landscape,facing(chapter_page(landscape,'先有观察，再有表达')),OUT/'editorial-landscape-spread.png')
    spread(portrait,[2,first-1],OUT/'editorial-after.png')
    before=OUT/'editorial-before/layout-lab-portrait.pdf'
    if before.exists():
        spread(before,[2,3],OUT/'editorial-before.png')

if __name__=='__main__':main()
