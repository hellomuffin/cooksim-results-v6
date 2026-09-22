"""Revision 3: sampled environment strips and continuous episode excerpts."""
from pathlib import Path
import json
from vector import Figure,INK,MUTED,LINE,BLUE,TEAL,RED,PALE_BLUE,PALE_TEAL,width
from build_teaser_foreign_lanes import role_icon

ROOT=Path(__file__).resolve().parent
PURPLE='#786387'

def dots(c,x,y,color=MUTED):
    for xx in (x-4,x,x+4):c.circle(xx,y,0.9,color,'none')

def environment():
    c=Figure('environments_v3',424,'Example tasks with layout context and sampled user-view sequences')
    c.text(16,17,'TASK',13,600,color=MUTED)
    c.text(202.5,17,'TOP-DOWN',13,600,anchor='middle',color=MUTED)
    c.text(276,17,'SELECTED EGOCENTRIC OBSERVATIONS',13,600,color=MUTED)
    c.arrow(600,13,776,13,MUTED,1)
    rows=[
      dict(y=25,engine='CookSim',color=TEAL,fill=PALE_TEAL,
           description='Assemble a burrito:\ncook rice and steak,\nchop the vegetables.',
           layout=('burrito_hard_real/initial.jpg',(48,78,850,668)),
           shots=[('revision3_nav_real/nav_14_09.jpg',(962,26,960,720),'Go to cutting board'),
                  ('burrito_hard_real/16.jpg',(1205,145,610,500),'Chop tomato'),
                  ('burrito_hard_real/25.jpg',(1160,210,620,480),'Turn on pan'),
                  ('burrito_hard_real/31.jpg',(1120,210,650,534),'Scoop rice')]),
      dict(y=134,engine='VHSim',color=PURPLE,fill='#F2EDF6',
           description='Clear dishes, return\nthe pillow, and turn\noff the TV for guests.',
           layout=('guest_hard/15_end.png',(640,26,480,454)),
           shots=[('guest_hard/02_mid_ego.png',(0,0,640,480),'Walk to kitchen'),
                  ('guest_hard/03_end_ego.png',(66,180,475,300),'Open dishwasher'),
                  ('guest_hard/06_grasp_ego.png',(175,150,330,330),'Pick up mug'),
                  ('guest_hard/13_end_ego.png',(25,45,575,435),'Put pillow on bed')])]
    for r in rows:
        y=r['y'];color=r['color']
        with c.group(r['engine']+' task description'):
            c.rect(8,y,146,104,r['fill'],'none',4)
            c.text(17,y+21,r['engine'],19,600,color=color)
            c.text(17,y+42,r['description'],14,leading=1.38)
        with c.group(r['engine']+' context, not a task step'):
            c.rect(164,y,77,104,'#F5F7F6',LINE,4,.6)
            c.photo_fit(167,y+7,71,71,*r['layout'],rounded=3,border=None)
            c.text(202.5,y+93,'Context map',12.5,anchor='middle',color=MUTED)
        c.path([(251,y+4),(251,y+98)],LINE,.8)
        for j,(src,crop,caption) in enumerate(r['shots']):
            x=268+j*130
            with c.group(r['engine']+' selected action '+str(j)):
                c.photo(x,y+4,114,75,src,crop,rounded=4,border=color)
                c.text(x+57,y+96,caption,14.5,anchor='middle',color=color)
            if j<3:dots(c,x+122,y+40)
        dots(c,781,y+40)
    y=260
    with c.group('ScreenSim task description'):
        c.rect(8,y,146,156,PALE_BLUE,'none',4)
        c.text(17,y+24,'ScreenSim',19,600,color=BLUE)
        c.text(17,y+50,'Make the phone\neasier to read:\nlarger, bolder text,\nhigher contrast,\nand less motion.',14,leading=1.4)
    c.text(164,258,'SELECTED SCREENS & TOUCH GESTURES',12.5,600,color=MUTED)
    manifest=json.loads((ROOT/'candidates/parent_phone_readability.json').read_text())
    # Real, complete phone screens. Gesture points come from the actual DOM
    # bounds of the widget acted on; only the illustrative hand is overlaid.
    screens=[(0,'s_access','Accessibility'),(1,'a_display','Display & text'),
             (2,'bold_text','Bold text'),(4,'text_size','Drag text size'),
             (10,'reduce_motion','Reduce motion'),(11,None,'Motion reduced')]
    # Resolve the actual widget IDs by their text, never guessed coordinates.
    queries=['Accessibility','Display & Text Size','Bold Text','Text Size','Reduce Motion',None]
    for j,((idx,_,caption),query) in enumerate(zip(screens,queries)):
        x=175+j*101;sy=271;w=60;h=130
        with c.group('ScreenSim full screen '+str(idx)):
            c.photo(x,sy,w,h,f'parent_phone_readability/{idx:02d}.png',(0,0,824,1784),rounded=5,border=LINE)
            if query:
                fs=manifest['frames'][idx]
                matches=[r for r in fs['widgets'] if r['text'].strip()==query or (query=='Text Size' and 'slider' in r['id'])]
                if not matches:matches=[r for r in fs['widgets'] if query in r['text']]
                assert matches,(idx,query)
                b=matches[-1]['raw_bounds'];tx=x+(b[0]+b[2]*.82)/824*w;ty=sy+(b[1]+b[3]/2)/1784*h
                if query=='Text Size':
                    # Native renderer: slider track is raw x=64..760, y=736.
                    # Illustrate the actual 50 -> 75 drag, not a generic swipe.
                    start=x+412/824*w;tx=x+586/824*w;ty=sy+736/1784*h
                    c.circle(start,ty,3.5,'none',BLUE,.7)
                c.circle(tx,ty,5.5,'#FFFFFF',BLUE,1)
                c.circle(tx,ty,2,BLUE,'none')
                if query=='Text Size':c.arrow(start,ty,tx,ty,BLUE,1.5)
                # Hand asset hotspot (158,32) in a 480 x 760 image.
                c.photo(tx-4.9375,ty-1,15,23.75,'revision3_assets/hand.png',border=None)
            if caption!='…':c.text(x+w/2,sy+h+14,caption,14,anchor='middle',color=BLUE)
        if j<5:
            if j in (2,3):dots(c,x+80,sy+64)
            else:c.arrow(x+69,sy+64,x+87,sy+64,MUTED,.9)
    c.save()

def speech(c,x,y,w,text,role='assistant',size=16):
    body=min(w-23,width(text,size)+14)
    if role=='user':
        role_icon(c,x+w-19,y+6,role)
        return c.bubble(x+w-23-body,y,body,text,role,size,pad=7)
    role_icon(c,x,y+6,role)
    return c.bubble(x+23,y,body,text,role,size,pad=7)

def snapshot(c,x,y,w,h,name,caption):
    crop=(1100,280,780,440)
    if name.endswith('_fresh_fish'):crop=(1145,425,700,230)
    c.photo(x,y,w,h,'revision3_fish_real/'+name+'.jpg',crop,rounded=4,border=LINE)
    c.rect(x,y+h,w,20,'#F2F5F4','none',0)
    c.text(x+w/2,y+h+14,caption,14,anchor='middle',color=TEAL)
    return h+20

def episodes():
    c=Figure('interaction_v3',570,'Episode excerpts: the same wrong-ingredient event under three assistants')
    c.rect(8,6,776,27,'#FAF0EC','none',4)
    c.text(19,25,'Simulated human error: wrong ingredient — lettuce instead of fried potato',15.5,600,color=RED)
    # Each assistant occupies ONE episode container. No category headings,
    # global flowchart, invented recipe panel, or pre-error user utterance.
    x=8;y=45;w=245
    with c.group('Assistant A episode excerpt'):
        c.rect(x,y,w,324,'#FFFFFF',LINE,5,.8)
        c.rect(x,y,w,27,PALE_BLUE,'none',5)
        c.text(x+12,y+19,'Assistant A',16,600,color=BLUE)
        dots(c,x+w-17,y+16)
        yy=y+37
        c.photo(x+12,yy,96,65,'revision3_fish_real/before_error.jpg',(1140,295,690,440),rounded=4)
        c.text(x+60,yy+80,'Approach lettuce',12.5,anchor='middle',color=TEAL)
        speech(c,x+116,yy,119,'Use chips, not lettuce.')
        yy+=92
        yy+=speech(c,x+10,yy,w-20,'Oh, right.','user')+8
        yy+=snapshot(c,x+12,yy,w-24,72,'correct_chips','Go to fryer → scoop chips')+9
        yy+=speech(c,x+10,yy,w-20,'Now take it to the pass.')+8
        c.text(x+35,yy+10,'Go to pass → serve',13.5,color=TEAL)
        dots(c,x+w-18,yy+6)
    with c.group('Assistant C episode excerpt'):
        y=381
        c.rect(x,y,w,180,'#FFFFFF',LINE,5,.8)
        c.rect(x,y,w,27,PALE_BLUE,'none',5)
        c.text(x+12,y+19,'Assistant C',16,600,color=BLUE)
        dots(c,x+w-17,y+16)
        yy=y+36
        yy+=speech(c,x+10,yy,w-20,'(silent)')+8
        yy+=snapshot(c,x+12,yy,w-24,60,'silent_at_pass','Scoop lettuce → go to pass')+8
        c.text(x+35,yy+10,'Serve → rejected',13.5,color=RED)
    with c.group('Assistant B shared episode and two user continuations'):
        x=266;y=45;w=518
        c.rect(x,y,w,516,'#FFFFFF',LINE,5,.8)
        c.rect(x,y,w,27,PALE_BLUE,'none',5)
        c.text(x+12,y+19,'Assistant B',16,600,color=BLUE)
        c.text(x+w-12,y+19,'Two user continuations',13.5,anchor='end',color=MUTED)
        snapshot(c,x+12,y+37,147,75,'wrong_lettuce','Scoop lettuce')
        speech(c,x+170,y+37,335,'You added lettuce, not chips. Empty the plate at the trash and start over.')
        for xx,label,sub in [(278,'High trust','Welcomes step-by-step guidance'),(532,'Low trust','Dislikes interruptions')]:
            with c.group(label+' episode continuation'):
                c.rect(xx,189,240,366,'#F9FBFA','#DCE5E0',4,.7)
                c.rect(xx,189,240,43,PALE_TEAL,'none',4)
                c.text(xx+10,207,label,15.5,600,color=TEAL)
                c.text(xx+10,225,sub,13.2,color=TEAL)
                yy=241
                if label=='High trust':
                    yy+=speech(c,xx+7,yy,226,'Got it, emptying the plate.','user')+7
                    yy+=snapshot(c,xx+13,yy,214,68,'high_empty','Go to trash → empty plate')+8
                    yy+=speech(c,xx+7,yy,226,'What’s next?','user')+7
                    yy+=speech(c,xx+7,yy,226,'Set the plate down and get a fresh fish.')+8
                    yy+=snapshot(c,xx+13,yy,214,61,'high_fresh_fish','Put down plate → fetch fish …')
                else:
                    yy+=speech(c,xx+7,yy,226,'Why throw it out? It’s just lettuce.','user')+4
                    yy+=speech(c,xx+7,yy,226,'The order needs fish and chips, with no lettuce.')+4
                    yy+=speech(c,xx+7,yy,226,'Fine, I’ll redo it.','user')+5
                    yy+=snapshot(c,xx+13,yy,214,55,'low_empty','Go to trash → empty plate')+5
                    yy+=speech(c,xx+7,yy,226,'Get a fresh fish.')+4
                    yy+=speech(c,xx+7,yy,226,'I know the rest.','user')+5
                    c.text(xx+22,548,'Restart independently …',14,color=TEAL)
    c.save()

if __name__=='__main__':environment();episodes()
