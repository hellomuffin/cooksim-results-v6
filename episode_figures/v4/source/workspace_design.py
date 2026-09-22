"""Wide paper panels; substantive, illustrative dialogue grounded in real logs.

Creates a new revision only. Published drawings and user edits are never inputs
to destructive regeneration. Observation crops retain original engine pixels.
"""
from pathlib import Path
import json
from vector import Figure, INK, MUTED, LINE, BLUE, TEAL, RED, PALE_BLUE, PALE_TEAL, wrap
from build_teaser_foreign_lanes import role_icon
from build_revision3 import dots

ROOT=Path(__file__).resolve().parent
PURPLE='#786387'

def bubble(c,x,y,w,text,role='assistant',size=15):
    """A role-marked horizontal utterance, with a compact outside icon."""
    role_icon(c,x,y+7,role)
    return c.bubble(x+23,y,w-23,text,role,size,pad=6)

def fish(c,x,y,w,h,name,caption,size=13.5):
    crop=(1100,280,780,440)
    if name=='before_error':crop=(1140,295,690,440)
    if name.endswith('_fresh_fish'):crop=(1145,425,700,230)
    c.photo(x,y,w,h,'revision3_fish_real/'+name+'.jpg',crop,rounded=3)
    c.text(x+w/2,y+h+15,caption,size,anchor='middle',color=TEAL)

def episodes():
    c=Figure('interaction_v4',436,'Wide episode excerpts with contextual dialogue and action consequences')
    c.rect(8,4,776,25,'#FAF0EC','none',4)
    c.text(18,22,'Simulated human error: wrong ingredient — lettuce instead of fried potato',15,600,color=RED)

    # The short A/C excerpts sit together; B receives the space its multi-turn
    # continuation needs. The bottom two strips are enclosed by B, not peers.
    with c.group('Assistant A episode'):
        c.rect(8,37,608,104,'#FFFFFF',LINE,4,.8)
        c.text(18,56,'Assistant A',15,600,color=BLUE)
        c.text(604,56,'…',15,anchor='end',color=MUTED)
        fish(c,18,65,77,48,'before_error','At lettuce',13)
        bubble(c,105,64,279,'Wait, that’s lettuce. Leave it there and scoop the chips from the fryer onto your fish.',size=14.5)
        bubble(c,390,64,132,'Oh, right. I’ll go to the fryer instead.','user',14.5)
        fish(c,530,65,76,48,'correct_chips','Scoop chips',13)
    with c.group('Assistant C episode'):
        c.rect(626,37,158,104,'#FFFFFF',LINE,4,.8)
        c.text(636,56,'Assistant C',15,600,color=BLUE)
        c.text(772,56,'…',15,anchor='end',color=MUTED)
        fish(c,636,64,70,44,'silent_at_pass','',13)
        bubble(c,712,66,65,'…',size=14.5)
        c.text(740,110,'Silent',13,anchor='middle',color=MUTED)
        c.text(705,131,'Serve → rejected',13,anchor='middle',color=RED)

    with c.group('Assistant B episode with two alternative continuations'):
        c.rect(8,151,776,277,'#FFFFFF',LINE,4,.8)
        c.text(18,170,'Assistant B',15,600,color=BLUE)
        fish(c,18,177,102,42,'wrong_lettuce','Scoop lettuce',13)
        bubble(c,135,177,636,'You’ve added lettuce instead of chips. That plate won’t match the order now. Take it to the trash and empty the contents; you’ll keep the plate.',size=15)
        c.text(772,169,'Two alternative user continuations',13,anchor='end',color=MUTED)
        with c.group('High trust and stepwise guidance'):
            c.rect(18,239,756,87,'#F7FAF8','none',4)
            c.text(28,255,'High trust · welcomes step-by-step guidance',13.5,600,color=TEAL)
            bubble(c,27,261,249,'Okay, I’ll empty it. Can you walk me through what to do next?','user',14.5)
            fish(c,288,261,87,39,'high_empty','Empty plate',13)
            bubble(c,389,261,374,'Set the empty plate on a counter, then pick up a fresh fish. We’ll cook that before plating again.',size=14.5)
        with c.group('Low trust and interruption aversion'):
            c.rect(18,331,756,88,'#F7FAF8','none',4)
            c.text(28,347,'Low trust · dislikes interruptions',13.5,600,color=TEAL)
            bubble(c,27,353,220,'Why throw it all out? The fish is already cooked—can’t I just take the lettuce off?','user',14.5)
            bubble(c,254,353,240,'You can only empty the whole plate here. It won’t pass as fish and chips with lettuce on it.',size=14.5)
            bubble(c,501,353,183,'All right, I’ll redo it. I can handle the steps from here.','user',14.5)
            fish(c,695,354,69,39,'low_empty','Empty plate',13)
    c.save()

def gesture(c,manifest,idx,query,x,y,w,h):
    fs=manifest['frames'][idx]
    matches=[r for r in fs['widgets'] if r['text'].strip()==query or (query=='Text Size' and 'slider' in r['id'])]
    if not matches:matches=[r for r in fs['widgets'] if query in r['text']]
    assert matches,(idx,query)
    b=matches[-1]['raw_bounds'];tx=x+(b[0]+b[2]*.82)/824*w;ty=y+(b[1]+b[3]/2)/1784*h
    if query=='Text Size':
        start=x+412/824*w;tx=x+586/824*w;ty=y+736/1784*h
        c.circle(start,ty,3,'none',BLUE,.7)
        c.arrow(start,ty,tx,ty,BLUE,1.3)
    c.circle(tx,ty,4.5,'#FFFFFF',BLUE,.9)
    c.circle(tx,ty,1.6,BLUE,'none')
    c.photo(tx-4.9375,ty-1,15,23.75,'revision3_assets/hand.png',border=None)

def episodes_flat():
    """Column labels replace header rows; all episode reading is left to right."""
    c=Figure('interaction_flat_v4',376,'Wide horizontal episodes with contextual dialogue and two user continuations')
    c.rect(8,4,776,25,'#FAF0EC','none',4)
    c.text(18,22,'Simulated human error: wrong ingredient — lettuce instead of fried potato',15,600,color=RED)
    with c.group('Assistant A episode excerpt'):
        c.rect(8,37,776,69,'#FFFFFF',LINE,4,.8)
        c.text(18,63,'Assistant\nA',14.5,600,color=BLUE,leading=1.4)
        fish(c,89,45,80,40,'before_error','At lettuce',13)
        bubble(c,180,45,330,'Wait, that’s lettuce. Leave it there and scoop the chips from the fryer onto your fish.',size=14.5)
        bubble(c,515,45,170,'Oh, right. I’ll go to the fryer instead.','user',14.5)
        fish(c,696,45,78,40,'correct_chips','Scoop chips',13)
    with c.group('Assistant B episode and two user continuations'):
        c.rect(8,115,776,214,'#FFFFFF',LINE,4,.8)
        c.text(18,141,'Assistant\nB',14.5,600,color=BLUE,leading=1.4)
        fish(c,89,123,80,39,'wrong_lettuce','Scoop lettuce',13)
        bubble(c,180,123,594,'You’ve added lettuce instead of chips. That plate won’t match the order now. Take it to the trash and empty the contents; you’ll keep the plate.',size=14.5)
        with c.group('High trust and step-by-step guidance'):
            c.rect(18,181,756,57,'#F7FAF8','none',3)
            c.text(27,199,'High trust',13.5,600,color=TEAL)
            c.text(27,219,'Step-by-step',13,color=TEAL)
            bubble(c,118,187,239,'Okay, I’ll empty it. What do I need to do next?','user',14.5)
            fish(c,368,187,76,32,'high_empty','Empty plate',13)
            bubble(c,456,187,308,'Set the plate on an empty counter, then fetch a fresh fish. We’ll cook that next.',size=14.5)
        with c.group('Low trust and interruption aversion'):
            c.rect(18,244,756,77,'#F7FAF8','none',3)
            c.text(27,262,'Low trust',13.5,600,color=TEAL)
            c.text(27,280,'Dislikes\ninterruptions',13,color=TEAL,leading=1.4)
            bubble(c,118,250,190,'Why throw the fish away too? Can’t I just take the lettuce off?','user',14.5)
            bubble(c,320,250,230,'It won’t match the order with lettuce on it. You can only empty the whole plate.',size=14.5)
            bubble(c,562,250,130,'Fine. I’ll take it from here.','user',14.5)
            fish(c,704,250,70,32,'low_empty','Empty plate',13)
    with c.group('Assistant C episode excerpt'):
        c.rect(8,339,776,29,'#FFFFFF',LINE,4,.8)
        c.text(18,358,'Assistant C',14.5,600,color=BLUE)
        role_icon(c,123,345,'assistant')
        c.text(151,358,'(silent)',14.5,color=MUTED)
        c.arrow(211,353,243,353,MUTED,1)
        c.text(255,358,'Scoop lettuce → go to pass → serve',14.5,color=TEAL)
        c.text(774,358,'Order rejected',14.5,anchor='end',color=RED)
    c.save()

def environments():
    c=Figure('environments_v4',290,'Three everyday-task environments in a wide, standalone paper panel')
    domains=[dict(x=8,engine='CookSim',color=TEAL,fill=PALE_TEAL,
        description='Assemble a burrito with cooked rice\nand steak, and chopped vegetables.',
        layout=('burrito_hard_real/initial.jpg',(48,78,850,668)),
        nav=('revision3_nav_real/nav_14_09.jpg',(962,26,960,720),'Go to cutting board'),
        shots=[('burrito_hard_real/16.jpg',(1205,145,610,500),'Chop\ntomato'),
               ('burrito_hard_real/25.jpg',(1160,210,620,480),'Turn on\npan'),
               ('burrito_hard_real/31.jpg',(1120,210,650,534),'Scoop rice')]),
        dict(x=270,engine='VHSim',color=PURPLE,fill='#F2EDF6',
        description='Prepare for guests: clear the dishes,\nreturn the pillow, and turn off the TV.',
        layout=('guest_hard/15_end.png',(640,26,480,454)),
        nav=('guest_hard/02_mid_ego.png',(0,0,640,480),'Walk to kitchen'),
        shots=[('guest_hard/03_end_ego.png',(66,180,475,300),'Open\ndishwasher'),
               ('guest_hard/06_grasp_ego.png',(175,150,330,330),'Pick up\nmug'),
               ('guest_hard/13_end_ego.png',(25,45,575,435),'Return\npillow')])]
    for d in domains:
        x=d['x'];color=d['color']
        with c.group(d['engine']+' environment'):
            c.rect(x,5,252,280,'#FFFFFF',LINE,5,.8)
            c.rect(x,5,252,69,d['fill'],'none',5)
            c.text(x+11,26,d['engine'],18,600,color=color)
            c.text(x+11,46,d['description'],14,leading=1.4)
            with c.group('Top-down context, not an action'):
                c.rect(x+9,85,73,96,'#F4F6F5','none',3)
                c.text(x+45.5,100,'TOP-DOWN',11.5,600,anchor='middle',color=MUTED)
                c.photo_fit(x+13,105,65,61,*d['layout'],rounded=2,border=None)
                c.text(x+45.5,177,'Context',11.5,anchor='middle',color=MUTED)
            with c.group('Navigation observation'):
                c.text(x+95,98,'EGOCENTRIC',11.5,600,color=MUTED)
                c.photo(x+95,106,147,59,*d['nav'][:2],rounded=3,border=color)
                c.text(x+168.5,181,d['nav'][2],13.5,anchor='middle',color=color)
            c.path([(x+94,189),(x+242,189)],LINE,.8)
            c.text(x+11,201,'…',15,color=MUTED)
            for j,(src,crop,label) in enumerate(d['shots']):
                xx=x+10+j*81
                with c.group('Selected action '+str(j)):
                    c.photo(xx,208,70,39,src,crop,rounded=3,border=color)
                    c.text(xx+35,259,label,14,anchor='middle',color=color,leading=1.4)
                if j<2:dots(c,xx+75.5,227)
            dots(c,x+245,227)
    with c.group('ScreenSim environment'):
        x=532
        c.rect(x,5,252,280,'#FFFFFF',LINE,5,.8)
        c.rect(x,5,252,69,PALE_BLUE,'none',5)
        c.text(x+11,26,'ScreenSim',18,600,color=BLUE)
        c.text(x+11,46,'Make the phone easier to read with\nlarger text, contrast, and less motion.',14,leading=1.4)
        c.text(x+11,98,'FULL SCREENS & TOUCH GESTURES',11.5,600,color=MUTED)
        manifest=json.loads((ROOT/'candidates/parent_phone_readability.json').read_text())
        for j,(idx,query,caption) in enumerate([(0,'Accessibility','Accessibility'),(1,'Display & Text Size','Display &\ntext'),(4,'Text Size','Text size'),(10,'Reduce Motion','Reduce\nmotion')]):
            xx=x+10+j*61;yy=117;w=48;h=w*1784/824
            c.photo(xx,yy,w,h,f'parent_phone_readability/{idx:02d}.png',(0,0,824,1784),rounded=4)
            gesture(c,manifest,idx,query,xx,yy,w,h)
            if j<3:
                if j==0:c.arrow(xx+51,yy+52,xx+57,yy+52,MUTED,.7)
                else:dots(c,xx+54,yy+52)
        c.text(x+64,241,'Navigate to\ndisplay settings',14,anchor='middle',color=BLUE,leading=1.4)
        c.text(x+156,241,'Enlarge\ntext',14,anchor='middle',color=BLUE,leading=1.4)
        c.text(x+217,241,'Reduce\nmotion',14,anchor='middle',color=BLUE,leading=1.4)
        c.text(x+126,278,'…',15,anchor='middle',color=MUTED)
    c.save()

if __name__=='__main__':environments();episodes();episodes_flat()
