"""Revision 3 arrangement, expanded frame strips, and connected error timelines."""
from pathlib import Path
import json
from vector5 import WideFigure,INK,MUTED,LINE,BLUE,COPPER,PALE_BLUE,PALE_COPPER
from vector import wrap

ROOT=Path(__file__).resolve().parent

def dots(c,x,y):
    for dx in (-7,0,7):c.circle(x+dx,y,1.8,MUTED,'none')

def role(c,x,y,user=False):
    color=COPPER if user else BLUE
    if user:
        c.circle(x+13,y+8,7,color,'none');c.rect(x+2,y+19,23,15,color,'none',7)
    else:
        c.rect(x,y+8,28,22,'#FFFFFF',color,6,2.5)
        c.circle(x+8,y+17,2.1,color,'none');c.circle(x+21,y+17,2.1,color,'none')
        c.path([(x+9,y+24),(x+20,y+24)],color,1.8)
        c.path([(x+14,y+8),(x+14,y+2)],color,2)
        c.circle(x+14,y,2.3,color,'none')

def speech(c,x,y,w,text,user=False,size=31,spine=None):
    role(c,x,y+9,user)
    if spine is not None:
        col=COPPER if user else BLUE
        c.circle(spine,y+27,4.5,col,'none')
        c.path([(spine+5,y+27),(x-8,y+27)],LINE,1.6)
    return c.bubble(x+42,y,w-42,text,'user' if user else 'assistant',size,pad=12)

def photo(c,x,y,w,h,name):
    crop=(1100,280,780,440)
    if name=='before_error':crop=(1140,295,690,440)
    if name.endswith('fresh_fish'):crop=(1145,425,700,230)
    c.photo(x,y,w,h,'revision3_fish_real/'+name+'.jpg',crop,rounded=9,border=LINE)

def event(c,x,y,text,color=BLUE,size=28):
    c.circle(x,y-9,6,'#FFFFFF',color,2.5)
    c.text(x+18,y,text,size,600,color=color)

def environments():
    c=WideFigure('environments_v5',718,'Everyday tasks: expanded observation strips',1600)
    c.text(20,31,'Task',29,600)
    c.text(374,31,'Top-down',27,600,anchor='middle',color=MUTED)
    c.text(460,31,'Sampled user-view observations',27,600,color=MUTED)
    c.arrow(1120,23,1566,23,MUTED,2)
    rows=[dict(y=51,engine='CookSim',color=COPPER,fill=PALE_COPPER,
      description='Cook rice and steak,\nchop vegetables, and\nassemble a burrito.',
      layout=('burrito_hard_real/initial.jpg',(48,78,850,668)),
      shots=[('burrito_hard_real/05.jpg',(962,26,960,720),'Pick up steak'),
      ('revision3_nav_real/nav_14_09.jpg',(962,26,960,720),'Go to\ncutting board'),
      ('burrito_hard_real/16.jpg',(1205,145,610,500),'Chop tomato'),
      ('burrito_hard_real/25.jpg',(1160,210,620,480),'Turn on pan'),
      ('burrito_hard_real/31.jpg',(1120,210,650,534),'Scoop rice'),
      ('burrito_hard_real/33.jpg',(1100,210,720,490),'Plate steak')]),
      dict(y=232,engine='VHSim',color=BLUE,fill=PALE_BLUE,
      description='Clear dishes, return\nthe pillow, and turn\noff the TV for guests.',
      layout=('guest_hard/15_end.png',(640,26,480,454)),
      shots=[('guest_hard/02_mid_ego.png',(0,0,640,480),'Walk to kitchen'),
      ('guest_hard/03_end_ego.png',(66,180,475,300),'Open\ndishwasher'),
      ('guest_hard/06_grasp_ego.png',(175,150,330,330),'Pick up mug'),
      ('guest_hard/08_end_ego.png',(66,180,475,300),'Put mug inside'),
      ('guest_hard/13_end_ego.png',(25,45,575,435),'Return pillow'),
      ('guest_hard/15_end_ego.png',(0,0,640,480),'Turn off TV')])]
    for d in rows:
        y=d['y'];col=d['color']
        with c.group(d['engine']+' task and sequence'):
            c.rect(12,y,310,165,d['fill'],col,11,2)
            c.text(27,y+35,d['engine'],33,600,color=col)
            c.text(27,y+71,d['description'],28,leading=1.33)
            c.rect(336,y+3,87,158,'#F5F5F1',LINE,10,1.6)
            c.photo_fit(340,y+13,79,105,*d['layout'],border=None,rounded=6)
            c.text(379.5,y+145,'Context',24,anchor='middle',color=MUTED)
            c.path([(443,y+9),(443,y+152)],LINE,1.8)
            for j,(src,crop,cap) in enumerate(d['shots']):
                x=461+j*188
                with c.group('Observation '+str(j+1)):
                    c.photo(x,y+7,164,104,src,crop,rounded=9,border=col)
                    c.text(x+82,y+143,cap,26,anchor='middle',color=col,leading=1.35)
                if j<5:dots(c,x+176,y+60)
            dots(c,1585,y+61)
    y=425;olive='#626642'
    with c.group('ScreenSim task and full screen navigation'):
        c.rect(12,y,310,279,'#F3F3E9',olive,11,2)
        c.text(27,y+36,'ScreenSim',33,600,color=olive)
        c.text(27,y+74,'Improve readability\nwith larger, bolder\ntext, more contrast,\nand less motion.',28,leading=1.35)
        manifest=json.loads((ROOT/'candidates/parent_phone_readability.json').read_text())
        selections=[(0,'Accessibility','Open\naccessibility'),(1,'Display & Text Size','Display &\ntext size'),
          (2,'Bold Text','Bold text'),(4,'Text Size','Larger text'),
          (6,'Button Shapes','Button\nshapes'),(7,'Increase Contrast','Contrast'),
          (10,'Reduce Motion','Reduce\nmotion'),(11,None,'Motion\nreduced')]
        for j,(idx,query,cap) in enumerate(selections):
            x=365+j*153;sy=438;w=88;h=w*1784/824
            c.photo(x,sy,w,h,f'parent_phone_readability/{idx:02d}.png',(0,0,824,1784),rounded=10,border=LINE)
            if query:
                fs=manifest['frames'][idx]
                matches=[r for r in fs['widgets'] if r['text'].strip()==query or (query=='Text Size' and 'slider' in r['id'])]
                if not matches:matches=[r for r in fs['widgets'] if query in r['text']]
                assert matches,(idx,query)
                b=matches[-1]['raw_bounds'];tx=x+(b[0]+b[2]*.82)/824*w;ty=sy+(b[1]+b[3]/2)/1784*h
                if query=='Text Size':
                    start=x+412/824*w;tx=x+586/824*w;ty=sy+736/1784*h
                    c.arrow(start,ty,tx,ty,BLUE,2)
                c.circle(tx,ty,6,'#FFFFFF',BLUE,1.7);c.circle(tx,ty,2.2,BLUE,'none')
                c.photo(tx-7.40625,ty-1.5,22.5,35.625,'revision3_assets/hand.png',border=None)
            c.text(x+44,sy+h+30,cap,26,anchor='middle',color=olive,leading=1.3)
            if j<7:dots(c,x+115,sy+85)
    c.save()

def episodes():
    c=WideFigure('interaction_v5',1034,'Error-event timelines and persona-dependent episode continuations')
    # A common event timeline, not a list of action names. Relative event order
    # is meaningful; horizontal distance is intentionally not measured latency.
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
    c.text(474,111,'A responds',25,color=BLUE)
    c.text(1299,111,'B responds',25,color=BLUE)
    # A receives a chance to intervene before commitment. B receives the late
    # message; C continues from the irreversible state without intervention.
    c.arrow(460,130,460,173,BLUE,2.5)
    c.arrow(1285,130,1285,173,BLUE,2.5)
    c.path([(750,130),(750,159),(536,159),(536,828),(510,828)],MUTED,2.2,True)

    with c.group('Assistant A episode before the irreversible error'):
        c.rect(16,179,494,608,'#FFFFFF',BLUE,13,2.5)
        c.rect(16,179,494,48,PALE_BLUE,'none',13)
        c.text(38,215,'Assistant A',34,600,color=BLUE)
        c.arrow(37,244,37,753,'#8A9BA5',2.3)
        y=245
        y+=speech(c,56,y,435,'Wait—that’s lettuce, not chips. You already have fish on the plate; get the chips from the fryer instead.',spine=37)+18
        y+=speech(c,56,y,435,'Oh, right. I went to the wrong station. I’ll get the chips instead.',True,spine=37)+16
        photo(c,190,y,224,92,'correct_chips')
        event(c,37,y+44,'',BLUE)
        c.text(302,y+125,'Error prevented',28,600,anchor='middle',color=BLUE)
    with c.group('Assistant C episode without an intervention'):
        c.rect(16,810,494,208,'#FFFFFF',LINE,13,2.5)
        c.rect(16,810,494,46,'#F2F4F4','none',13)
        c.text(38,845,'Assistant C',34,600,color=BLUE)
        c.text(43,897,'(silent)',30,color=MUTED)
        c.path([(38,917),(38,995),(161,995)],MUTED,2.5,True)
        photo(c,204,867,268,81,'silent_at_pass')
        c.text(338,979,'Error persists',27,600,anchor='middle',color=COPPER)
        c.text(178,1009,'Order rejected',29,600,color=COPPER)

    with c.group('Assistant B episode after the irreversible error'):
        c.rect(562,179,1222,839,'#FFFFFF',BLUE,13,2.5)
        c.rect(562,179,1222,48,PALE_BLUE,'none',13)
        c.text(584,215,'Assistant B',34,600,color=BLUE)
        c.text(1760,214,'Two user continuations',27,anchor='end',color=MUTED)
        speech(c,585,244,1177,'You’ve added lettuce instead of chips. The plate won’t match the order now, and you can’t remove just the lettuce. Take it to the trash and empty the contents; you’ll keep the plate.')
        c.path([(1173,387),(1173,395),(872,395),(872,400)],LINE,2,True)
        c.path([(1173,395),(1470,395),(1470,400)],LINE,2,True)
        for x,high in [(583,True),(1181,False)]:
            with c.group('High trust / stepwise guidance' if high else 'Low trust / dislikes interruptions'):
                c.rect(x,402,578,598,'#FFFFFF',COPPER,11,2)
                c.rect(x,402,578,81,PALE_COPPER,'none',11)
                c.text(x+20,437,'High trust' if high else 'Low trust',32,600,color=COPPER)
                c.text(x+20,470,'Welcomes step-by-step guidance' if high else 'Dislikes interruptions',27,color=COPPER)
                c.arrow(x+23,501,x+23,978,'#8A9BA5',2.3)
                y=502
                if high:
                    y+=speech(c,x+45,y,509,'Okay, I’ll empty it. Can you walk me through what I should do to start again?',True,spine=x+23)+12
                    photo(c,x+178,y,250,84,'high_empty')
                    event(c,x+23,y+38,'',COPPER)
                    c.text(x+303,y+114,'Recovery begins',27,600,anchor='middle',color=COPPER)
                    y+=138
                    y+=speech(c,x+45,y,509,'Set the plate on an empty counter, then fetch a fresh fish. We’ll cook that next.',spine=x+23)+12
                    c.text(x+63,y+24,'…',30,color=MUTED)
                else:
                    y+=speech(c,x+45,y,509,'Why throw the fish away too? It’s already cooked. Can’t I just take the lettuce off?',True,spine=x+23)+12
                    y+=speech(c,x+45,y,509,'You can only empty the whole plate here. It won’t pass as fish and chips with lettuce on it.',spine=x+23)+12
                    y+=speech(c,x+45,y,509,'Fine. I’ll take it from here.',True,spine=x+23)+12
                    photo(c,x+178,y,250,84,'low_empty')
                    event(c,x+23,y+38,'',COPPER)
                    c.text(x+303,y+113,'Recovery begins',27,600,anchor='middle',color=COPPER)
    c.save()

if __name__=='__main__':environments();episodes()
