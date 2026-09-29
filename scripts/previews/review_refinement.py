"""Compare real PDF pages. Optional baselines live in exports/refinement-review/before."""
from pathlib import Path
import argparse
import html
import json
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('sidebar', 'layout-lab', 'a4', '复盘是一种编辑能力', False, '细长图与正文并排'),
    ('closing', 'layout-lab', 'a4', '从读者关系到价值交付', True, '章节收尾回到同页'),
    ('notes', 'layout-lab', 'a4', '排版实验与阅读边界', True, '短注释跟随正文'),
    ('pair-portrait', 'shore-and-space', 'portrait', '清晰之外还有什么', False, '竖版：横竖图底边对齐'),
    ('pair-landscape', 'shore-and-space', 'landscape', '清晰之外还有什么', False, '横版：双图与图注对齐'),
    ('pair-a4', 'shore-and-space', 'a4', '清晰之外还有什么', False, 'A4：完整画幅与留白'),
]

AESTHETIC_CASES = [
    ('editorial-cover', 'layout-lab', 'portrait', '', False, '内容的复利：封面层级'),
    ('editorial-opening', 'layout-lab', 'portrait', '先有观察，再有表达', False, '内容的复利：章首与阅读节奏'),
    ('editorial-method', 'layout-lab', 'a4', '搭建内容工作系统', False, '内容的复利：图表与方法页'),
    ('spectacle-cover', 'desire-manufacture', 'portrait', '', False, '欲望制造：封面细节与色彩'),
    ('spectacle-opening', 'desire-manufacture', 'portrait', '一张广告图的内部秩序', False, '欲望制造：长章名与宣言'),
    ('spectacle-landscape', 'desire-manufacture', 'landscape', '一张广告图的内部秩序', False, '欲望制造：横版章首'),
    ('spectacle-table', 'desire-manufacture', 'portrait', '让人记住', False, '欲望制造：章首与正文'),
]

SPECTACLE_CASES = [
    ('cover', 'desire-manufacture', 'portrait', '', False, '摄影杂志封面'),
    ('opening', 'desire-manufacture', 'portrait', '先被看见', False, '章首接入正文'),
    ('long-title', 'desire-manufacture', 'portrait', '一张广告图的内部秩序', False, '长章名与阅读节奏'),
    ('landscape-cover', 'desire-manufacture', 'landscape', '', False, '横版封面'),
    ('landscape', 'desire-manufacture', 'landscape', '值得渴望', False, '横版图文'),
]

def chapter_page(doc, title, last):
    # Chapter destinations are collected from the PDF outline, not fixed page numbers.
    if not title:
        return 0
    toc = [(label, page) for level, label, page in doc.get_toc() if level == 1]
    index = next(i for i, (label, _) in enumerate(toc) if label == title)
    if last == 'reading':
        return toc[index][1]
    return toc[index + 1][1] - 2 if last and index + 1 < len(toc) else toc[index][1] - 1

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--focus', choices=['paper', 'aesthetics', 'spectacle', 'tension'], default='paper')
    args = parser.parse_args()
    OUT = ROOT / 'exports' / {'paper':'refinement-review', 'aesthetics':'aesthetic-review', 'spectacle':'spectacle-redesign', 'tension':'spectacle-tension'}[args.focus]
    cases = {'paper':CASES, 'aesthetics':AESTHETIC_CASES, 'spectacle':SPECTACLE_CASES, 'tension':SPECTACLE_CASES}[args.focus]
    intro = ('《内容的复利》与《欲望制造》的封面、章首、色彩与正文精修。' if args.focus == 'aesthetics'
             else '《内容的复利》的图文关系与短注释；《岸与间》的双图底边与图注。')
    if args.focus == 'spectacle':
        intro = '《欲望制造》重新设计为奢侈品摄影杂志：大幅图像、暖白纸面、酒红色字排，章首直接接入正文。'
    if args.focus == 'tension':
        intro = '《欲望制造》构图精修：偏置大图、跨越图像边界的刊头、叠压书名，以及章首与引文的尺度反差。'
    OUT.mkdir(parents=True, exist_ok=True)
    sections, reports = [], []
    for key, slug, profile, title, last, label in cases:
        filename = f'{slug}-{profile}.pdf'
        figures = []
        for edition, source in [('before', OUT / 'before' / filename), ('after', ROOT / 'exports' / slug / filename)]:
            if not source.exists():
                continue
            with fitz.open(source) as doc:
                page = chapter_page(doc, title, last)
                image = f'{key}-{edition}.png'
                doc[page].get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False).save(OUT / image)
                caption = f'{"修改前" if edition == "before" else "修改后"} · 第 {page + 1} 页 / 全书 {len(doc)} 页'
                reports.append(dict(case=key, edition=edition, page=page+1, total=len(doc)))
                figures.append(f'<figure><figcaption>{caption}</figcaption><a href="{image}"><img src="{image}" alt="{html.escape(label)}，{caption}" loading="lazy"></a></figure>')
        sections.append(f'<section><h2>{html.escape(label)}</h2><p>{html.escape(title or "封面")} · {profile}</p><div class="comparison">{"".join(figures)}</div></section>')
    (OUT / 'pages.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2))
    (OUT / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>纸本细节 · 实际书页对照</title><style>
*{box-sizing:border-box}body{margin:0;background:#e8e5df;color:#292722;font-family:serif}main{max-width:1440px;margin:auto;padding:40px}h1,h2{font-weight:normal}h1{font-size:36px}p{line-height:1.8}a{color:inherit}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:28px}section{border-top:1px solid #bcb5a8;margin-top:48px;padding-top:24px}figure{margin:0;min-width:0}figcaption{font:13px/1.8 sans-serif;margin-bottom:12px}img{display:block;width:100%;height:auto}@media(max-width:700px){main{padding:20px}h1{font-size:28px}.comparison{grid-template-columns:1fr}}
</style></head><body><main><p><a href="../index.html">作品书架</a></p><h1>纸本细节 · 实际书页对照</h1><p>''' + intro + '''图片全部来自真实 PDF，原稿与素材未改动。修改前样张仅在本地保留了旧 PDF 时显示。</p>''' + ''.join(sections) + '</main></body></html>')
    print(OUT / 'index.html')

if __name__ == '__main__':
    main()
