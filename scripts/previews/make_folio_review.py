"""Render actual FOLIO PDF pages and facing pages for the design preview."""
from pathlib import Path
import json
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]

def main():
    folder=ROOT/'exports/shore-and-space'
    out=folder/'previews'; out.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype(str(ROOT/'design/fonts/NotoSansSC-Regular.ttf'),20)
    report={}
    for profile in ['portrait','landscape','a4']:
        with fitz.open(folder/f'shore-and-space-{profile}.pdf') as doc:
            toc={title:page-1 for level,title,page in doc.get_toc()}
            titles=['先看见一条线','房间里的远方','四次回声','观看发生在两张图之间','把最后一点光留下']
            indices=[0]+[toc[t] for t in titles]
            expansion_titles=['让颜色暂时退场','向上，也向内','红色先于房子抵达','颜色也有重量','夜晚借来的颜色','把蓝换一种温度','绿色不是一种颜色','浅色如何留下边界','清晰之外还有什么','叶子留下另一种蓝','把不同颜色放在同一页','一本书可以容纳几种声音']
            expansion=[toc[t] for t in expansion_titles]
            for suffix,selected,labels in [('board',indices,['封面']+titles),('color-board',expansion,expansion_titles)]:
                board=Image.new('RGB',(1500,540*((len(selected)+2)//3)),'#e6e6e2')
                draw=ImageDraw.Draw(board)
                for i,index in enumerate(selected):
                    pix=doc[index].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False)
                    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
                    im.thumbnail((460,460))
                    x=20+(i%3)*500; y=20+(i//3)*540
                    board.paste(im,(x+(460-im.width)//2,y))
                    draw.text((x,y+480),f'{index+1:02d} / '+labels[i],font=font,fill='#444949')
                board.save(out/f'{profile}-{suffix}.png')
            # Even PDF page on the left, its following odd page on the right.
            first=toc['房间里的远方']; left=first if first%2==1 else first-1
            images=[]
            for index in [left,left+1]:
                pix=doc[index].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False)
                images.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
            spread=Image.new('RGB',(sum(im.width for im in images)+4,max(im.height for im in images)),'#ddddda')
            spread.paste(images[0],(0,0)); spread.paste(images[1],(images[0].width+4,0))
            spread.save(out/f'{profile}-spread.png')
            report[profile]={'pages':len(doc),'sample_pages':[i+1 for i in indices],'color_pages':[i+1 for i in expansion],'facing_pages':[left+1,left+2]}
    (out/'folio-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
