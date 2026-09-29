"""Rebuild original vector illustrations for the expanded sample books.
Only writes vault/assets/longform-lab. All numerical examples are synthetic.
"""
from pathlib import Path
import json
from make_finance_samples import text as outline_text, rect, line, save
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'vault/assets/longform-lab'
def text(x, y, value, size=20, color='#343a33'):
    # At 110–115 mm print width this keeps labels around 6 pt or larger.
    return outline_text(x, y, value, max(size, 20), color)

PAPER='#f4f0e6'; INK='#343a33'; BLUE='#1545ba'; GREEN='#25483e'; GOLD='#a67d3f'

def flow(filename,title,labels,subtitles,color=INK):
    s=rect(0,0,1000,380,PAPER)+text(36,55,title,28,color)
    w=(928-(len(labels)-1)*24)/len(labels)
    for n,(label,sub) in enumerate(zip(labels,subtitles)):
        x=36+n*(w+24)
        s+=line(x,113,x+w,113,color,2)+text(x,148,f'0{n+1}',16,GOLD)+text(x,210,label,24,color)+text(x,252,sub,14,color)
        if n<len(labels)-1:s+=line(x+w+4,198,x+w+20,198,GOLD,2)
    s+=text(36,338,'CONCEPT STUDY / 原创概念图 · 非实测数据',14,color)
    save(OUT/filename,1000,380,title,s)

def generate():
    flow('editorial-evidence.svg','让一段判断找得到来处',['材料','核对','解释','行动'],['保存原始情境','检查范围与来源','区分事实和推断','留出修订入口'])
    flow('editorial-channels.svg','一个观点，五种阅读入口',['长文','社群','视频','邮件','练习'],['展开完整问题','邀请经验补充','展示具体差异','继续已有对话','留下操作结果'])
    flow('business-service.svg','一份服务的四个决定',['需求','确认','制作','使用'],['问题怎样发生','谁决定信息','谁完成交付','谁更新材料'],BLUE)
    flow('desire-sequence.svg','从第一眼，到真正使用',['看见','理解','决定','打开','使用'],['主体与场景','信息与边界','规格与条件','顺序与说明','反馈与修订'],'#ae251e')
    flow('investment-horizons.svg','先让资金用途变得具体',['用途','时点','空间','复核'],['准备支持什么','何时可能使用','哪些条件可调','何时重新检查'],GREEN)
    s=rect(0,0,900,570,PAPER)
    s+=rect(80,65,345,440,'#fffdf7','#bdb5a8')+rect(440,65,345,440,'#fffdf7','#bdb5a8')
    for x in [110,470]:
        for n in range(13):s+=line(x,180+n*19,x+190-(n%4)*12,180+n*19,'#a9a596',2)
        s+=line(x+220,170,x+220,442,'#b9afa0')+text(x,130,'READ / RETURN',17,INK)
    s+=rect(701,249,24,130,'#e7dcc9')+text(80,546,'正文、页边与尚未完成的空白',18,INK)
    save(OUT/'notes-margins.svg',900,570,'抽象书页：正文、页边与空白',s)
    s=rect(0,0,900,640,PAPER)+rect(92,98,360,430,'#8a9585')+rect(110,98,8,430,'#556653')
    for n in range(7):s+=line(151,195+n*38,388,195+n*38,'#e3e3d6',2)
    s+=f'<circle cx="635" cy="235" r="90" fill="#ddd0b8"/><circle cx="635" cy="235" r="68" fill="#79715e"/><path d="M714 185 Q820 195 717 285" fill="none" stroke="#ddd0b8" stroke-width="18"/>'
    s+='<path d="M541 427 L787 487" stroke="#a67d3f" stroke-width="12"/><path d="M787 487 L812 493 L794 475" fill="#343a33"/>'
    s+=text(95,589,'OBJECT STUDIES / 一张桌面的三个位置',19,INK)
    save(OUT/'notes-objects.svg',900,640,'笔记本、铅笔与杯子的原创几何静物',s)
    s=rect(0,0,900,610,PAPER)
    for n,(label,color) in enumerate([('春','#92a48a'),('夏','#527d69'),('秋','#b08c54'),('冬','#a5aaa7')]):
        x=50+(n%2)*420;y=40+(n//2)*280
        s+=rect(x,y,375,240,color)+text(x+22,y+55,label,32,'#fffdf7')
        for k in range(3):s+=line(x+30,y+112+k*40,x+340,y+112+k*40,'#fffdf7')+text(x+32,y+100+k*40,f'{n*3+k+1:02d}',14,'#fffdf7')
    save(OUT/'notes-seasons.svg',900,610,'四季与十二个记录位置的抽象插画',s)
    s=rect(0,0,960,440,PAPER)+text(35,52,'虚构项目 / 40 小时怎样分布',26,BLUE)
    vals=[('资料核对',12),('正文编辑',14),('视觉排版',8),('校对交付',6)]
    for n,(label,v) in enumerate(vals):
        y=105+n*70;s+=text(35,y+25,label,19,BLUE)+rect(210,y,v*37,36,['#1545ba','#496bc7','#8299d4','#b7c5e4'][n])+text(225+v*37,y+26,f'{v} h',18,BLUE)
    s+=text(35,416,'虚构工时 · 不含等待时间 · 非行业标准',15,BLUE)
    save(OUT/'business-capacity.svg',960,440,'虚构40小时项目：资料12小时，编辑14小时，排版8小时，校对6小时',s)
    balances=[20000,22000,15000,22000,18000]
    s=rect(0,0,960,470,PAPER)+text(35,48,'现金在什么时候到达',27,BLUE)+text(35,82,'虚构余额 · 单位：元 · 不是利润',15,BLUE)
    for v in [10000,15000,20000,25000]:
        y=365-(v-10000)/60;s+=line(100,y,900,y,'#d8d1bc')+text(25,y+4,str(v),13,BLUE)
    pts=[(110+n*190,365-(v-10000)/60) for n,v in enumerate(balances)]
    s+='<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+'" fill="none" stroke="#1545ba" stroke-width="3"/>'
    for n,(x,y) in enumerate(pts):s+=f'<circle cx="{x}" cy="{y}" r="5" fill="#1545ba"/>'+text(x-24,y-15,str(balances[n]),14,BLUE)+text(x-22,410,['月初','一周','二周','三周','四周'][n],15,BLUE)
    save(OUT/'business-cash.svg',960,470,'虚构现金余额：20000、22000、15000、22000、18000元',s)
    s=''
    for n,(bg,fg,label) in enumerate([('#080808','#f4f0e6','BLACK'),('#ee2d20','#080808','RED'),(PAPER,'#080808','PAPER')]):
        x=n*300;s+=rect(x,0,300,520,bg)+rect(x+100,125,100,215,'none',fg,2)+line(x+100,190,x+200,190,fg,2)+text(x+35,410,label,31,fg)+text(x+35,461,'SAME OBJECT',15,fg)
    save(OUT/'desire-contrast.svg',900,520,'同一几何物件在黑、红与米纸背景中的对照',s)
    paths=[[100,105,110,115,120],[100,130,90,110,120]]
    s=rect(0,0,960,500,PAPER)+text(35,48,'相同终点，不同路径',27,GREEN)
    for v in [80,90,100,110,120,130,140]:
        y=380-(v-80)*4;s+=line(90,y,905,y,'#d8d1bc')+text(37,y+5,str(v),14,GREEN)
    for n,values in enumerate(paths):
        pts=[(100+k*195,380-(v-80)*4) for k,v in enumerate(values)]
        color=[GREEN,GOLD][n];s+='<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="3"/>'
        for k,(x,y) in enumerate(pts):s+=f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>'
        s+=line(40+n*270,452,85+n*270,452,color,3)+text(95+n*270,458,['甲 / 平稳上升','乙 / 先升后落再恢复'][n],17,color)
    for k in range(5):s+=text(96+k*195,409,str(k),13,GREEN)
    s+=text(650,460,'虚构路径 · 非真实行情',14,GREEN)
    save(OUT/'investment-paths.svg',960,500,'虚构路径甲100、105、110、115、120；乙100、130、90、110、120',s)
    s=rect(0,0,960,470,PAPER)+text(35,48,'不同名称，仍然可能重叠',27,GREEN)
    for n,(label,weights) in enumerate([('组合甲',[.5,.5,0]),('组合乙',[.5,0,.5]),('各投入一半',[.5,.25,.25])]):
        y=110+n*90;x=215;s+=text(35,y+32,label,20,GREEN)
        for k,w in enumerate(weights):
            if w:
                s+=rect(x,y,w*660,48,[GREEN,'#8d9f91',GOLD][k])+text(x+12,y+32,f'{["X","Y","Z"][k]} {w:.0%}',20,'#fffdf7');x+=w*660
    s+=text(35,441,'虚构权重 · X / Y / Z 为占位符 · 不代表任何产品',15,GREEN)
    save(OUT/'investment-overlap.svg',960,470,'虚构重叠演示：组合甲X50%Y50%，乙X50%Z50%，等额合并X50%Y25%Z25%',s)
    (OUT/'data.json').write_text(json.dumps(dict(cash_balances=balances,cash_received=[8000,0,16000,4000],cash_paid=[6000,7000,9000,8000],hours=dict(vals),paths=paths,path_b_max_drawdown=1-90/130,overlap=[.5,.25,.25]),ensure_ascii=False,indent=2))
    (OUT/'SOURCE.md').write_text('本目录全部 SVG 为 scripts/assets/make_longform_assets.py 原创矢量图或几何插画，字形使用 Noto Sans SC（OFL）轮廓。所有经营、工时、现金与投资数据为明确设定的虚构演示，不使用真实公司或市场资料。数值输入保存在 data.json。插画不对应真实人物或地点。\n')

if __name__=='__main__':generate()
