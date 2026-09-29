"""Compose previews directly from exported PDF pages; no mockup decoration."""
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]

def main():
    font=ImageFont.truetype(str(ROOT/'design/fonts/NotoSansSC-Regular.ttf'),24)
    samples=[('business-architecture',['找到付费的理由','把交付变成流程','看清一单的结构']),('through-volatility',['读懂一次回撤','费用怎样进入时间','怎样阅读一份投资材料'])]
    for slug,titles in samples:
        doc=pymupdf.open(ROOT/f'exports/{slug}/{slug}-portrait.pdf')
        toc={title:page-1 for _,title,page in doc.get_toc()}
        pages=[0]+[toc[title] for title in titles]
        board=Image.new('RGB',(1680,650),'#e8e4dc')
        draw=ImageDraw.Draw(board)
        for i,index in enumerate(pages):
            pix=doc[index].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4),alpha=False)
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            im.thumbnail((390,566))
            x=20+i*420
            board.paste(im,(x,20))
            draw.text((x,598),f'{index+1:02d} / '+('封面' if index==0 else '内页'),font=font,fill='#575249')
        board.save(ROOT/f'exports/{slug}/previews/design-board.png')
    books=['layout-lab','field-notes','desire-manufacture','business-architecture','through-volatility']
    board=Image.new('RGB',(1800,580),'#e8e4dc')
    draw=ImageDraw.Draw(board)
    for i,slug in enumerate(books):
        im=Image.open(ROOT/f'exports/{slug}/cover.png').convert('RGB')
        im.thumbnail((320,470))
        x=20+i*360
        board.paste(im,(x,20))
        label=['摄影书刊','极简随笔','奢华影像','商业蓝图','投资年鉴'][i]
        draw.text((x,510),f'0{i+1} / {label}',font=font,fill='#575249')
    out=ROOT/'exports/visual-review'
    out.mkdir(exist_ok=True)
    board.save(out/'five-designs.png')

if __name__=='__main__': main()
