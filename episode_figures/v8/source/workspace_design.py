"""Color-led task strips, large maps, and four consecutive executable actions."""
from pathlib import Path
import json
from vector5 import WideFigure,INK,MUTED,LINE
from vector import width
ROOT=Path(__file__).resolve().parent
COLORS=[('#315E89','#EBF3FB'),('#635585','#F1EDF8'),('#9B632C','#FFF2E2')]
XS=[392,650,908,1166,1530]

def omit(c,x,y,col):
    for dx in (-14,0,14):c.circle(x+dx,y,2.8,col,'none')

def strip(c,y,engine,description,col,pale):
    c.rect(14,y,1772,43,pale,'none',10)
    c.rect(14,y,137,43,col,'none',10)
    c.text(82.5,y+29,engine,22,600,anchor='middle',color='#FFFFFF')
    assert width(description,33,'Manrope SemiBold')<1600
    c.text(170,y+32,description,33,600,color=INK)

def command(c,x,y,w,text,col,pale):
    c.rect(x,y,w,66,pale,'none',8)
    lines=text.split('\n');base=y+(30 if len(lines)>1 else 43)
    assert all(width(line,28,'Manrope SemiBold')<=w-14 for line in lines),(text,w)
    c.text(x+w/2,base,text,28,600,anchor='middle',color=col,leading=1.17)

def main():
    c=WideFigure('environments_v8',1066,'Procedural tasks with individually attached action labels',1800)
    rows=[dict(y=12,engine='CookSim',description='Cook rice and steak, chop vegetables, and assemble a burrito.',
      layout=('burrito_hard_real/initial.jpg',(58,84,842,650)),
      shots=[('burrito_hard_real/13.jpg',(962,26,960,720),'pick up'),
      ('revision3_nav_real/nav_14_09.jpg',(962,26,960,720),'go to nearest\ncutting board'),
      ('burrito_hard_real/15.jpg',(1080,150,800,570),'put down'),
      ('burrito_hard_real/16.jpg',(1080,150,800,570),'chop'),
      ('burrito_hard_real/39.jpg',(962,26,960,720),'serve')]),
      dict(y=354,engine='VHSim',description='Prepare the home for guests: clear dishes, return the pillow, and switch off the TV.',
      layout=('guest_hard/15_end.png',(644,103,474,272)),
      shots=[('guest_hard/05_mid_ego.png',(0,0,640,480),'go to mug'),
      ('guest_hard/06_grasp_ego.png',(115,130,435,325),'pick up mug'),
      ('guest_hard/07_mid_ego.png',(0,0,640,480),'go to dishwasher'),
      ('guest_hard/08_end_ego.png',(66,180,475,300),'put mug in\ndishwasher'),
      ('guest_hard/15_end_ego.png',(0,0,640,480),'switch off tv')])]
    for k,d in enumerate(rows):
        col,pale=COLORS[k];y=d['y'];sy=y+73
        with c.group(d['engine']+' task and consecutive action strip'):
            strip(c,y,d['engine'],d['description'],col,pale)
            c.photo_fit(18,sy,324,250,*d['layout'],border=None,rounded=8)
            c.text(180,y+65,'Top-down',22,600,anchor='middle',color=col)
            c.path([(369,sy),(369,sy+251)],col,2.2)
            for j,(src,crop,cap) in enumerate(d['shots']):
                with c.group('Action '+str(j+1)):
                    command(c,XS[j],sy+177,244,cap,col,pale)
                    c.rect(XS[j],sy+173,244,13,pale,'none',0)
                    c.photo(XS[j],sy,244,181,src,crop,rounded=8,border=LINE)
            omit(c,1468,sy+92,col)
    col,pale=COLORS[2];y=693;sy=y+73
    manifest=json.loads((ROOT/'candidates/revision7_phone.json').read_text())
    with c.group('ScreenSim four consecutive gestures and a final gesture'):
        strip(c,y,'ScreenSim','Improve readability with bold, larger text, increased contrast, and reduced motion.',col,pale)
        # Full-screen locator establishes the two half-screen viewport choices.
        fw=106;fh=fw*1784/824;fx=70;fy=sy+4
        c.photo(fx,fy,fw,fh,'revision7_phone/00.png',(0,0,824,1784),rounded=12,border=LINE)
        c.rect(fx-3,fy+fh/2,fw+6,fh/2,'none',col,5,2.4)
        c.path([(fx+fw+7,fy+fh*.25),(214,fy+fh*.25)],col,1.7)
        c.path([(fx+fw+7,fy+fh*.75),(214,fy+fh*.75)],col,1.7)
        c.text(226,fy+fh*.25+8,'Upper half',23,color=col)
        c.text(226,fy+fh*.75+8,'Lower half',23,color=col)
        c.text(180,y+65,'Screen regions',22,600,anchor='middle',color=col)
        c.path([(369,sy),(369,sy+251)],col,2.2)
        chosen=[(0,'Accessibility','tap Accessibility',892),(1,'Display & Text Size','tap Display &\nText Size',0),
                (2,'Larger Text','tap Larger Text',0),(3,'Text Size','swipe right on\nText Size',0),
                (10,'Reduce Motion','tap Reduce\nMotion',0)]
        # Keep the exact half-screen aspect ratio, centered over each command.
        pw=190;ph=pw*892/824
        for j,(idx,query,label,cy) in enumerate(chosen):
            x=XS[j]+(244-pw)/2
            command(c,XS[j],sy+ph-1,244,label,col,pale)
            c.rect(x,sy+ph-10,pw,15,pale,'none',0)
            c.photo(x,sy,pw,ph,f'revision7_phone/{idx:02d}.png',(0,cy,824,892),rounded=8,border=LINE)
            fs=manifest['frames'][idx]
            matches=[r for r in fs['widgets'] if r['text'].split('\n')[0]==query]
            assert len(matches)==1,(idx,query,matches)
            b=matches[0]['raw_bounds'];rx=b[0]+b[2]*.82;ry=b[1]+b[3]/2
            if query=='Text Size':rx=586;ry=736
            tx=x+rx/824*pw;ty=sy+(ry-cy)/892*ph
            assert sy<=ty<=sy+ph,(idx,ty)
            c.circle(tx,ty,6.2,'#FFFFFF',col,2);c.circle(tx,ty,2.2,col,'none')
            if query=='Text Size':c.arrow(x+412/824*pw,ty,tx-6,ty,col,2.5)
            # Near an edge use the ring alone; never let a hand obscure the label below.
            if ty+37<sy+ph:
                c.photo(tx-8.9,ty-1.8,27,42.75,'revision3_assets/hand.png',border=None)
        omit(c,1468,sy+105,col)
    c.save()

if __name__=='__main__':main()
