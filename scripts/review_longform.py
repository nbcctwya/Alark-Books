"""Summarize expanded sample books and render representative real PDF pages.
Reads vault and exports; writes only exports/longform-review.
"""
from pathlib import Path
import re,json,html
import pymupdf
import yaml
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'exports/longform-review'
BOOKS=['layout-lab','field-notes','desire-manufacture','business-architecture','through-volatility']
BASELINE={'layout-lab':[18,19,15],'field-notes':[8,8,6],'desire-manufacture':[19,19,15],'business-architecture':[12,14,11],'through-volatility':[13,14,12]}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype(str(ROOT/'design/fonts/NotoSansSC-Regular.ttf'),20)
    reports=[]
    for slug in BOOKS:
        folder=ROOT/'vault/books'/slug
        meta=yaml.safe_load((folder/'book.yml').read_text())
        source='\n'.join((folder/ch).read_text() for ch in meta['chapters'])
        report=dict(slug=slug,title=meta['title'],chapters=len(meta['chapters']),chinese_characters=len(re.findall(r'[\u4e00-\u9fff]',source)),figures=len(re.findall(r'!\[',source)),baseline_pages=BASELINE[slug],profiles={})
        for profile in ['portrait','landscape','a4']:
            with pymupdf.open(ROOT/f'exports/{slug}/{slug}-{profile}.pdf') as doc:
                pages=[]
                for n,p in enumerate(doc):
                    txt=p.get_text()
                    chars=len(re.findall(r'[\u4e00-\u9fff]',txt))
                    # Dense vector paths identify outlined SVG illustrations; page rules are much simpler.
                    has_art=bool(p.get_image_info()) or bool(re.search(r'图\s*\d+[-－—]\d+', txt))
                    pages.append(dict(page=n+1,chinese_characters=chars,art=has_art))
                dense=[p['page'] for p in pages if p['chinese_characters']>=500]
                mixed=[p['page'] for p in pages if p['art'] and p['chinese_characters']>=100 and p['page']>3]
                report['profiles'][profile]=dict(pages=len(doc),dense_pages=dense,mixed_pages=mixed,max_chinese_characters=max(p['chinese_characters'] for p in pages))
                if profile=='portrait':
                    rank=sorted(pages[3:],key=lambda p:p['chinese_characters'],reverse=True)
                    chosen=[]
                    for num in [rank[0]['page'],*(mixed[-2:]),rank[1]['page'],rank[2]['page']]:
                        if num not in chosen:chosen.append(num)
                        if len(chosen)==4:break
                    report['preview_pages']=chosen
                    sheet=Image.new('RGB',(1760,680),'#e7e3db');draw=ImageDraw.Draw(sheet)
                    for k,n in enumerate(chosen):
                        pix=doc[n-1].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4),alpha=False)
                        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((410,596))
                        x=15+k*440;sheet.paste(im,(x,15));draw.text((x,630),f'P. {n:02d} / '+('图文组合' if n in mixed else '连续正文'),font=font,fill='#393b35')
                    sheet.save(OUT/f'{slug}.png')
        reports.append(report)
    (OUT/'report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
    doc='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>五本长篇样书 · 排版审阅</title><style>@font-face{font-family:Ark;src:url('../../design/fonts/NotoSerifSC-Regular.ttf')}*{box-sizing:border-box}body{margin:0;background:#f5f2eb;color:#292722;font-family:Ark,serif}main{max-width:1380px;padding:40px;margin:auto}h1{font-size:36px;font-weight:400}h2{font-size:27px;font-weight:400}p{line-height:1.9}a{color:inherit;text-underline-offset:5px}section{border-top:1px solid #bab3a6;margin-top:55px;padding-top:25px}img{width:100%;display:block;margin-top:25px}.links{display:flex;flex-wrap:wrap;gap:20px;font-size:13px}.meta{font:13px/1.9 system-ui;color:#686357}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:12px;border-bottom:1px solid #ccc4b7}@media(max-width:600px){main{padding:20px}h1{font-size:27px}table{font-size:11px}th,td{padding:8px 4px}}</style></head><body><main><p><a href="../index.html">返回作品书架</a></p><h1>五本长篇样书 · 排版审阅</h1><p>密集正文、图文组合、访谈、长表格与注释。每张样张都来自实际导出的 PDF。所有新增人物、经营案例与演算数据均为原创虚构示例。</p><table><thead><tr><th>书名</th><th>章数</th><th>中文字符</th><th>竖版页数变化</th><th>横版 / A4</th></tr></thead><tbody>'''
    for r in reports:
        p=r['profiles'];slug=r['slug'];doc+=f'<tr><td>{html.escape(r["title"])}</td><td>{r["chapters"]}</td><td>{r["chinese_characters"]:,}</td><td>{r["baseline_pages"][0]} → {p["portrait"]["pages"]}</td><td>{p["landscape"]["pages"]} / {p["a4"]["pages"]}</td></tr>'
    doc+='</tbody></table>'
    for r in reports:
        slug=r['slug'];p=r['profiles']['portrait']
        doc+=f'<section><h2>{html.escape(r["title"])}</h2><p class="meta">{r["chapters"]} 章 · 约 {r["chinese_characters"]:,} 中文字符（含标题、注释与配置段） · 竖版 {p["pages"]} 页 · 单页最多 {p["max_chinese_characters"]} 中文字符</p><div class="links">'
        for suffix,label in [('portrait.pdf','竖版 PDF'),('landscape.pdf','横版 PDF'),('a4.pdf','A4 PDF')]:doc+=f'<a href="../{slug}/{slug}-{suffix}">{label}</a>'
        doc+=f'<a href="../{slug}/{slug}.epub">EPUB</a><a href="../{slug}/previews/portrait-contact.png">全书缩略图</a></div><a href="../{slug}/{slug}-portrait.pdf"><img src="{slug}.png" alt="{html.escape(r["title"])}的实际正文与图文页面"></a></section>'
    doc+='<p class="meta">密集页按每页至少 500 个中文字符统计；图文检测用于抽样，不代替人工审阅。原始计数见 report.json。</p></main></body></html>'
    (OUT/'index.html').write_text(doc)
    for r in reports:print(r['slug'],r['chapters'],r['chinese_characters'],{k:v['pages'] for k,v in r['profiles'].items()})

if __name__=='__main__':main()
