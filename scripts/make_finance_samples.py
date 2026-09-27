"""Original vector diagrams. All chart observations are synthetic design examples.
Text is converted to outlines for portable Chinese rendering in SVG images.
"""
from pathlib import Path
from html import escape
import json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
ROOT=Path(__file__).resolve().parents[1]
FONT=TTFont(ROOT/'design/fonts/NotoSansSC-Regular.ttf')
GLYPHS=FONT.getGlyphSet(); CMAP=FONT.getBestCmap(); UPM=FONT['head'].unitsPerEm
BLUE='#1545ba'; ORANGE='#e57539'; GREEN='#25483e'; GOLD='#a67d3f'; PAPER='#f4f0e6'

def text(x,y,value,size=20,color=BLUE):
    pieces=[];advance=0
    for char in value:
        name=CMAP.get(ord(char),'space');pen=SVGPathPen(GLYPHS);GLYPHS[name].draw(pen)
        pieces.append(f'<path d="{pen.getCommands()}" transform="translate({advance} 0)"/>')
        advance+=FONT['hmtx'][name][0]
    return f'<g fill="{color}" transform="translate({x} {y}) scale({size/UPM} {-size/UPM})">'+''.join(pieces)+'</g>'

def rect(x,y,w,h,fill,stroke='none',width=1):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
def line(x1,y1,x2,y2,color,width=1,dash=''):return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def save(path,w,h,title,body):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>'+body+'</svg>',encoding='utf-8')

def generate():
    b=ROOT/'vault/assets/business-architecture';i=ROOT/'vault/assets/through-volatility'
    s=''
    for x in range(0,801,40):s+=line(x,0,x,520,'#dbe3f5')
    for y in range(0,521,40):s+=line(0,y,800,y,'#dbe3f5')
    for x,y,w,h in [(65,70,175,130),(310,180,175,130),(555,290,175,130)]:
        s+=rect(x,y,w,h,'#f8f9f5',BLUE,2)+line(x,y+35,x+w,y+35,BLUE)
    s+=line(240,135,397,135,BLUE,2)+line(397,135,397,180,BLUE,2)+line(485,245,642,245,BLUE,2)+line(642,245,642,290,BLUE,2)
    s+=rect(310,70,24,24,ORANGE)+rect(555,180,24,24,ORANGE)+rect(65,290,130,130,'none',BLUE)
    for n,(x,y,word) in enumerate([(80,100,'需求'),(325,210,'交付'),(570,320,'现金')],1):
        s+=text(x,y,word,19)+text(x,y+65,f'0{n}',36)
    s+=text(66,465,'BUSINESS IS A SYSTEM.',16)+line(65,486,730,486,BLUE)
    save(b/'blueprint.svg',800,520,'需求、交付与现金构成经营结构',s)
    s=rect(0,0,900,320,'#f7f8f3')+text(25,40,'一张订单的路径',25)+text(25,73,'概念示意 · 从承诺到回款',14,'#5d6678')
    for n,(title,subtitle) in enumerate([('理解需求','解决一个具体问题'),('形成方案','约定范围与结果'),('完成交付','检查承诺的兑现'),('收到回款','回到下一次经营')]):
        x=25+n*225;s+=rect(x,112,175,125,'none',BLUE,1.5)+text(x+12,141,f'0{n+1}',15,ORANGE)+text(x+12,181,title,22)+text(x+12,215,subtitle,12)
        if n<3:s+=line(x+180,173,x+215,173,BLUE,2)+line(x+210,168,x+215,173,BLUE,2)+line(x+215,173,x+210,178,BLUE,2)
    s+=line(790,254,790,283,ORANGE)+line(790,283,105,283,ORANGE)+line(105,283,105,254,ORANGE)+text(338,306,'反馈进入下一轮',13,ORANGE)
    save(b/'order-loop.svg',900,320,'订单路径：理解需求、形成方案、完成交付、收到回款；反馈进入下一轮',s)
    s=rect(0,0,900,390,'#f7f8f3')+text(28,43,'一单生意，留下多少空间？',25)+text(28,78,'虚构示例 · 单位：元 · 不含税费及其他未列项目',13,'#5d6678')
    values=[('收入',10000),('直接成本',6000),('履约后贡献',4000)]
    for n,(label,val) in enumerate(values):
        y=116+n*74;s+=text(28,y+28,label,17)+rect(190,y,620*val/10000,40,BLUE if n!=1 else '#91a8d8')+text(205+620*val/10000,y+28,f'{val:,}',18,ORANGE)
    s+=text(28,369,'贡献 4,000 元仍需覆盖固定费用，并不等于净利润。',16)
    save(b/'unit-economics.svg',900,390,'虚构订单：收入10000，直接成本6000，贡献4000，尚未扣除固定费用',s)
    vals=[100,108,103,116,95,92,108,124,118,132,126,142,131,145]
    s=''
    for y in [90,160,230,300,370]:s+=line(40,y,770,y,'#d8d1bc')
    pts=[(45+n*55,370-(v-90)*4.5) for n,v in enumerate(vals)]
    s+='<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{GREEN}" stroke-width="3"/>'
    for x,y in pts:s+=f'<circle cx="{x}" cy="{y}" r="4" fill="{GREEN}"/>'
    s+=line(40,400,770,400,GOLD)+text(43,434,'TIME / RISK / DISCIPLINE',19,GREEN)+text(43,469,'概念曲线 · 非实际市场数据',13,GOLD)
    save(i/'horizon.svg',800,490,'概念时间曲线，展示波动，不代表任何实际资产',s)
    path=[100,110,120,108,96,102,114,126];drawdown=[v/max(path[:n+1])-1 for n,v in enumerate(path)]
    s=rect(0,0,900,500,PAPER)+text(32,42,'从高点到低点，再到恢复',25,GREEN)+text(32,77,'虚构路径 · 初始值 100 · 按每期收盘值计算',14,'#6e7467')
    for v in [90,100,110,120,130]:
        y=267-(v-90)*3.6;s+=line(85,y,850,y,'#d8d1bc')+text(34,y+5,str(v),13,GREEN)
    pts=[(90+n*106,267-(v-90)*3.6) for n,v in enumerate(path)]
    s+='<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{GREEN}" stroke-width="3"/>'
    for n,(x,y) in enumerate(pts):s+=f'<circle cx="{x}" cy="{y}" r="4" fill="{GREEN}"/>'+text(x-14,y-12,str(path[n]),13,GREEN)+text(x-6,300,str(n),12,GREEN)
    s+=text(30,344,'回撤',15,GOLD)+line(85,327,850,327,GOLD)
    for n,dd in enumerate(drawdown):
        x=90+n*106;s+=rect(x-18,328,36,abs(dd)*300,GOLD)+text(x-25,420,f'{dd:.0%}',12,GREEN)
    s+=text(32,477,'样本最大回撤：20%  /  从 96 回到 120，需要上涨 25%。',17,GREEN)
    save(i/'drawdown.svg',900,500,'虚构路径100、110、120、108、96、102、114、126；最大回撤20%，从96恢复至120需上涨25%',s)
    fees=[0,.005,.015];ends=[100*((1.04)*(1-f))**20 for f in fees]
    s=rect(0,0,900,420,PAPER)+text(30,43,'同一条假设收益路径，三种费用',25,GREEN)+text(30,80,'初始值 100 · 每年费用前增长 4% · 年末按资产值扣费 · 持续 20 年',13,'#6e7467')
    for n,(fee,end) in enumerate(zip(fees,ends)):
        y=126+n*80;s+=text(30,y+25,f'年费 {fee:.1%}',18,GREEN)+rect(195,y,500*end/max(ends),36,[GREEN,'#809285',GOLD][n])+text(210+500*end/max(ends),y+26,f'{end:.2f}',19,GREEN)
    s+=text(30,393,'数学演示，不是收益预测；未考虑税、交易成本与现金流。',14,GREEN)
    save(i/'fee-drag.svg',900,420,'费用演示，20年末值分别为'+','.join(f'{x:.2f}' for x in ends),s)
    (i/'data.json').write_text(json.dumps(dict(path=path,drawdowns=drawdown,fees=fees,ending_values=ends,formula='100 * (1.04 * (1-fee)) ** 20'),indent=2),encoding='utf-8')
    for dest in [b,i]:
        (dest/'SOURCE.md').write_text('本目录 SVG 由 scripts/make_finance_samples.py 原创生成。全部数字均为虚构演示或明确假设下的数学计算，不使用实际市场或公司数据。中文转为 Noto Sans SC（OFL）字形轮廓，跨 PDF/EPUB 渲染一致。投资演示输入与输出保存在 data.json。\n',encoding='utf-8')
if __name__=='__main__':generate()
