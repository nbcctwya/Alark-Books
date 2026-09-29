"""Rebuild original sample illustrations only. Does not write any manuscripts."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'vault/assets/layout-lab'
FONT = ROOT / 'design/fonts/NotoSansSC-Regular.ttf'
S = 3
INK, PAPER, RED, GRAY = '#202a29', '#f8f5ee', '#b44330', '#68736c'
def font(size): return ImageFont.truetype(str(FONT), int(size*S))
def canvas(w, h):
    im = Image.new('RGB', (w*S, h*S), PAPER)
    return im, ImageDraw.Draw(im)
def text(d, x, y, value, size=18, color=INK): d.text((x*S,y*S), value, font=font(size), fill=color)
def line(d, coords, fill=INK, width=1): d.line(tuple(v*S for v in coords), fill=fill, width=width*S)

def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    im,d=canvas(960,380)
    text(d,30,22,'从内容到信任，再到持续交付',26)
    text(d,30,66,'一个可复盘的内容商业循环 / 示意图',13,GRAY)
    labels=[('01','观察','记录真实问题'),('02','表达','形成可用内容'),('03','连接','让对话发生'),('04','交付','验证真实价值')]
    for i,(num,title,desc) in enumerate(labels):
        x=30+i*234
        d.rectangle((x*S,123*S,(x+198)*S,285*S), fill=INK if i==0 else '#eae6dc')
        color=PAPER if i==0 else INK
        text(d,x+18,137,num,16,RED if i else '#f2b19c')
        text(d,x+18,171,title,30,color)
        text(d,x+18,229,desc,14,color)
        if i<3:
            line(d,(x+204,200,x+226,200),RED,2)
            line(d,(x+221,195,x+226,200,x+221,205),RED,2)
    line(d,(831,303,831,337,132,337,132,303),RED,1)
    text(d,340,342,'反馈，让下一轮更准确',13,RED)
    im.save(OUT/'content-loop.png',dpi=(300,300))
    im,d=canvas(900,470)
    text(d,30,18,'产出更多，不一定积累更多',26)
    text(d,30,59,'测试数据 · 两种工作方式的内容复用次数',13,GRAY)
    for val in range(0,61,15):
        y=374-val*4.3
        line(d,(85,y,855,y),'#d9d4c8')
        text(d,38,y-10,str(val),13,GRAY)
    for i,(a,b) in enumerate(zip([12,19,22,24],[14,28,43,57])):
        x=151+i*178
        d.rectangle((x*S,(374-a*4.3)*S,(x+38)*S,374*S), fill='#aeb8ad')
        d.rectangle(((x+47)*S,(374-b*4.3)*S,(x+85)*S,374*S), fill=RED)
        text(d,x+7,384,f'第{i+1}周',14)
        text(d,x+48,374-b*4.3-27,str(b),14,RED)
    text(d,230,432,'灰绿：临时生成',13,GRAY)
    text(d,470,432,'朱红：素材库 + 复盘',13,RED)
    im.save(OUT/'reuse-chart.png',dpi=(300,300))
    im,d=canvas(900,340)
    for i in range(25):
        y=120+i*9
        points=[]
        for x in range(0,901,4):
            yy=y+math.sin(x/160+i*.12)*36+math.cos(x/310)*22
            points.append((x*S,yy*S))
        d.line(points,fill='#9eafa4' if i%3 else INK,width=2)
    d.ellipse((664*S,45*S,730*S,111*S),fill=RED)
    text(d,35,24,'让信息沉淀为自己的地形。',24)
    im.save(OUT/'landscape.png',dpi=(300,300))
    im,d=canvas(360,780)
    text(d,27,28,'一页复盘',30)
    text(d,27,80,'每周，为判断留下证据',14,GRAY)
    for i,label in enumerate(['本周观察','一次实验','读者反馈','下周调整']):
        y=155+i*142
        text(d,27,y,f'0{i+1} / {label}',18,RED)
        for j in range(3): line(d,(27,y+53+j*23,333,y+53+j*23),'#cbcbbf')
    im.save(OUT/'review-card.png',dpi=(300,300))
    (OUT/'SOURCE.md').write_text('这里的四张 PNG 均由 scripts/assets/make_samples.py 原创绘制。图表数字为虚构的排版测试数据，不构成研究结论。字体采用 Noto Sans SC（SIL OFL 1.1）。可随本项目使用、修改、分发。\n',encoding='utf-8')
if __name__=='__main__': generate()
