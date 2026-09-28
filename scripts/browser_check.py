"""Visual smoke checks for the bookshelf, design guide, HTML and EPUB XHTML."""
from pathlib import Path
import json
import zipfile
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports/visual-review'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ROOT/'exports/layout-lab/layout-lab.epub') as archive:
        archive.extractall(OUT/'epub-unpacked')
    cases = [
        ('bookshelf', ROOT/'exports/index.html'),
        ('design', ROOT/'design/visual-system.html'),
        ('reading', ROOT/'exports/layout-lab/layout-lab-portrait.html'),
        ('landscape-reading', ROOT/'exports/layout-lab/layout-lab-landscape.html'),
        ('epub-chapter', OUT/'epub-unpacked/EPUB/ch-02.xhtml'),
    ]
    spectacle = ROOT/'exports/desire-manufacture'
    if (spectacle/'desire-manufacture.epub').exists():
        with zipfile.ZipFile(spectacle/'desire-manufacture.epub') as archive:
            archive.extractall(OUT/'spectacle-epub-unpacked')
        cases += [
            ('spectacle-design', ROOT/'design/spectacle.html'),
            ('spectacle', spectacle/'desire-manufacture-portrait.html'),
            ('spectacle-landscape', spectacle/'desire-manufacture-landscape.html'),
            ('spectacle-epub', OUT/'spectacle-epub-unpacked/EPUB/ch-01.xhtml'),
        ]
    for slug in ['business-architecture', 'through-volatility']:
        folder=ROOT/'exports'/slug
        with zipfile.ZipFile(folder/f'{slug}.epub') as archive:
            archive.extractall(OUT/f'{slug}-epub')
        cases += [(slug, folder/f'{slug}-portrait.html'),
                  (slug+'-landscape', folder/f'{slug}-landscape.html'),
                  (slug+'-epub', OUT/f'{slug}-epub/EPUB/ch-02.xhtml')]
    cases.append(('five-designs', ROOT/'design/five-designs.html'))
    cases += [('editorial-refinement', ROOT/'design/editorial-refinement.html'), ('field-notes', ROOT/'exports/field-notes/field-notes-portrait.html')]
    cases.append(('longform-review', ROOT/'exports/longform-review/index.html'))
    for slug in ['layout-lab','field-notes','desire-manufacture','business-architecture','through-volatility']:
        dest=OUT/(slug+'-longform-epub')
        with zipfile.ZipFile(ROOT/'exports'/slug/f'{slug}.epub') as archive:
            archive.extractall(dest)
        chapter='ch-08.xhtml' if slug!='field-notes' else 'ch-03.xhtml'
        cases.append((slug+'-longform-epub', dest/'EPUB'/chapter))
    reports=[]
    folio=ROOT/'exports/shore-and-space'
    if (folio/'shore-and-space.epub').exists():
        dest=OUT/'folio-epub'
        with zipfile.ZipFile(folio/'shore-and-space.epub') as archive:
            archive.extractall(dest)
        cases += [('folio-design', ROOT/'design/folio.html')]
        cases += [('folio-'+profile, folio/f'shore-and-space-{profile}.html') for profile in ['portrait','landscape','a4']]
        cases += [('folio-epub-'+chapter, dest/'EPUB'/f'ch-{chapter}.xhtml') for chapter in ['03','04','09','10','12','14','16','20','22','23']]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, args=['--no-sandbox'])
        for label, path in cases:
            for width in [1440,390]:
                page=browser.new_page(viewport={'width':width,'height':1000 if width>600 else 844}, device_scale_factor=1)
                page.goto(path.as_uri(), wait_until='load')
                page.evaluate('document.fonts.ready')
                metrics=page.evaluate('''() => ({width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
                    brokenImages: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i=>i.src),
                    fonts: [...document.fonts].map(f=>({family:f.family,status:f.status}))})''')
                page.screenshot(path=str(OUT/f'{label}-{width}.png'), full_page=label in ['bookshelf','design'])
                metrics.update(page=label)
                reports.append(metrics)
                page.close()
        browser.close()
    (OUT/'browser-checks.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    errors=[r for r in reports if r['scrollWidth']>r['width'] or r['brokenImages'] or any(f['status']=='error' for f in r['fonts'])]
    print(json.dumps({'cases':len(reports),'errors':errors},ensure_ascii=False,indent=2))
    return bool(errors)
if __name__=='__main__': raise SystemExit(main())
