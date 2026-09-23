"""Larger paired observations and two assistant branches; preserve v5 masters."""
from pathlib import Path
import json
from vector5 import WideFigure,INK,MUTED,LINE,BLUE,COPPER,PALE_BLUE,PALE_COPPER
from build_revision5 import speech,photo,event
ROOT=Path(__file__).resolve().parent

def omission(c,x,y):
    for dx in (-13,0,13):c.circle(x+dx,y,2.6,MUTED,'none')

def environments():
    c=WideFigure('environments_v6',925,'Paired observations from procedural tasks',1800)
    c.text(20,31,'Task',28,600)
    c.text(347,31,'Top-down',27,600,anchor='middle',color=MUTED)
    c.text(468,31,'Sampled user-view observations',27,600,color=MUTED)
    c.arrow(1150,23,1752,23,MUTED,2)
    xs=[468,704,1000,1236,1532]
    rows=[dict(y=55,engine='CookSim',description='Cook rice and\nsteak, chop\nvegetables, and\nmake a burrito.',
      layout=('burrito_hard_real/initial.jpg',(48,78,850,668)),
      shots=[('burrito_hard_real/13.jpg',(962,26,960,720),'Pick up tomato'),
      ('revision3_nav_real/nav_14_09.jpg',(962,26,960,720),'Go to\ncutting board'),
      ('burrito_hard_real/24.jpg',(962,26,960,720),'Go to pan'),
      ('burrito_hard_real/25.jpg',(1160,170,650,500),'Turn on pan'),
      ('burrito_hard_real/38.jpg',(1050,180,840,555),'Bring dish\nto serving pass')]),
      dict(y=285,engine='VHSim',description='Clear dishes;\nreturn the pillow\nand turn off the\nTV for guests.',
      layout=('guest_hard/15_end.png',(640,26,480,454)),
      shots=[('guest_hard/02_mid_ego.png',(0,0,640,480),'Walk to kitchen'),
      ('guest_hard/03_end_ego.png',(66,180,475,300),'Open dishwasher'),
      ('guest_hard/12_mid_ego.png',(0,0,640,480),'Walk to bedroom'),
      ('guest_hard/13_end_ego.png',(25,45,575,435),'Return pillow'),
      ('guest_hard/15_end_ego.png',(0,0,640,480),'Turn off TV')])]
    for d in rows:
        y=d['y']
        with c.group(d['engine']+' paired observation sequence'):
            c.rect(12,y,232,216,'#F4F5F6','#A7B1B8',10,1.5)
            c.text(26,y+31,d['engine'],27,600,color=MUTED)
            c.text(26,y+70,d['description'],28,leading=1.32)
            c.photo_fit(258,y+5,178,177,*d['layout'],border=None,rounded=7)
            c.path([(450,y+2),(450,y+187)],MUTED,2.5)
            for j,(src,crop,cap) in enumerate(d['shots']):
                with c.group('Observation '+str(j+1)):
                    c.photo(xs[j],y+5,220,150,src,crop,rounded=9,border=LINE)
                    c.text(xs[j]+110,y+191,cap,27,anchor='middle',color=INK,leading=1.3)
            omission(c,962,y+80);omission(c,1514,y+80)
    with c.group('ScreenSim paired navigation and text-size observations'):
        y=525
        c.rect(12,y,232,216,'#F4F5F6','#A7B1B8',10,1.5)
        c.text(26,y+31,'ScreenSim',27,600,color=MUTED)
        c.text(26,y+70,'Enlarge text,\nuse bold type,\nboost contrast,\nreduce motion.',28,leading=1.32)
        manifest=json.loads((ROOT/'candidates/parent_phone_readability.json').read_text())
        selections=[(0,'Accessibility','Open\naccessibility'),(1,'Display & Text Size','Display &\ntext size'),
                    (4,'Text Size','Enlarge text'),(5,None,'Text enlarged'),(11,None,'Motion reduced')]
        px=[330,564,918,1152,1545];w=142;h=w*1784/824
        for j,(idx,query,cap) in enumerate(selections):
            x=px[j];sy=y+7
            c.photo(x,sy,w,h,f'parent_phone_readability/{idx:02d}.png',(0,0,824,1784),rounded=11,border=LINE)
            if query:
                fs=manifest['frames'][idx]
                matches=[r for r in fs['widgets'] if r['text'].strip()==query or (query=='Text Size' and 'slider' in r['id'])]
                if not matches:matches=[r for r in fs['widgets'] if query in r['text']]
                b=matches[-1]['raw_bounds'];tx=x+(b[0]+b[2]*.82)/824*w;ty=sy+(b[1]+b[3]/2)/1784*h
                if query=='Text Size':
                    start=x+412/824*w;tx=x+586/824*w;ty=sy+736/1784*h
                    c.arrow(start,ty,tx,ty,BLUE,2.5)
                c.circle(tx,ty,7,'#FFFFFF',BLUE,1.8);c.circle(tx,ty,2.6,BLUE,'none')
                c.photo(tx-10.37,ty-2.1,31.5,49.875,'revision3_assets/hand.png',border=None)
            c.text(x+w/2,sy+h+36,cap,27,anchor='middle',color=INK)
        omission(c,812,y+158);omission(c,1419,y+158)
    c.save()

def episodes():
    c=WideFigure('interaction_v6',989,'Two assistant responses on an error-event timeline')
    c.rect(16,7,1768,143,'#FAFAF7',LINE,12,1.5)
    photo(c,115,21,158,81,'before_error')
    c.text(294,48,'Error begins',31,600,color=COPPER)
    c.text(294,85,'Lettuce instead of chips',28,color=MUTED)
    photo(c,671,21,158,81,'wrong_lettuce')
    c.text(849,48,'Point of no return',31,600,color=COPPER)
    c.text(849,85,'Lettuce added to the plate',28,color=MUTED)
    c.text(1406,48,'Episode time',27,600,color=MUTED)
    c.text(1450,84,'Not to scale',24,color=MUTED)
    c.arrow(51,120,1750,120,MUTED,2.5)
    for xx in (210,460,750,1285):c.circle(xx,120,8,'#FFFFFF',COPPER if xx in (210,750) else BLUE,3)
    c.text(474,111,'A responds',25,color=BLUE);c.text(1299,111,'B responds',25,color=BLUE)
    c.arrow(460,130,460,173,BLUE,2.5);c.arrow(1285,130,1285,173,BLUE,2.5)
    with c.group('Assistant A episode'):
        c.rect(16,179,494,793,'#FFFFFF',BLUE,13,2.5)
        c.rect(16,179,494,48,PALE_BLUE,'none',13)
        c.text(38,215,'Assistant A',34,600,color=BLUE)
        c.arrow(37,244,37,923,'#8A9BA5',2.3)
        y=245
        y+=speech(c,56,y,435,'Wait, are you going to add lettuce? This order is fish and chips. You already have the fish; get the chips from the fryer instead.',spine=37)+18
        y+=speech(c,56,y,435,'Oh, right. I went to the wrong station. I’ll get the chips instead.',True,spine=37)+25
        photo(c,100,y,360,177,'correct_chips');event(c,37,y+75,'',BLUE)
        c.text(280,y+214,'Error prevented',28,600,anchor='middle',color=BLUE)
    with c.group('Assistant B and two user continuations'):
        c.rect(562,179,1222,793,'#FFFFFF',BLUE,13,2.5)
        c.rect(562,179,1222,48,PALE_BLUE,'none',13)
        c.text(584,215,'Assistant B',34,600,color=BLUE)
        c.text(1760,214,'Two user continuations',27,anchor='end',color=MUTED)
        h=speech(c,585,244,1177,'You’ve added lettuce instead of chips. That doesn’t match the fish-and-chips order. Empty the plate into the trash, then start again with fish and chips.')
        c.path([(1173,244+h+4),(1173,363),(872,363),(872,373)],LINE,2,True)
        c.path([(1173,363),(1470,363),(1470,373)],LINE,2,True)
        for x,high in [(583,True),(1181,False)]:
            with c.group('User: high trust in AI' if high else 'User: low trust in AI'):
                c.rect(x,375,578,579,'#FFFFFF',COPPER,11,2)
                c.rect(x,375,578,51,PALE_COPPER,'none',11)
                c.text(x+20,411,'User: high trust in AI' if high else 'User: low trust in AI',31,600,color=COPPER)
                c.arrow(x+23,444,x+23,917,'#8A9BA5',2.3)
                y=445
                if high:
                    y+=speech(c,x+45,y,509,'Okay, I’ll empty it. Can you walk me through what I should do to start again?',True,spine=x+23)+12
                    photo(c,x+178,y,250,84,'high_empty');event(c,x+23,y+38,'',COPPER)
                    c.text(x+303,y+114,'Recovery begins',27,600,anchor='middle',color=COPPER)
                    y+=138
                    y+=speech(c,x+45,y,509,'Set the plate on an empty counter, then fetch a fresh fish. We’ll cook that next.',spine=x+23)+12
                    c.text(x+63,y+24,'…',30,color=MUTED)
                else:
                    y+=speech(c,x+45,y,509,'Are you sure? I thought I followed the order. Check the plate again.',True,spine=x+23)+12
                    y+=speech(c,x+45,y,509,'The green leaves are lettuce. The order calls for fish and chips, not lettuce.',spine=x+23)+12
                    y+=speech(c,x+45,y,509,'All right, I see it now. I’ll restart.',True,spine=x+23)+12
                    photo(c,x+178,y,250,84,'low_empty');event(c,x+23,y+38,'',COPPER)
                    c.text(x+303,y+113,'Recovery begins',27,600,anchor='middle',color=COPPER)
    c.save()

if __name__=='__main__':environments();episodes()
