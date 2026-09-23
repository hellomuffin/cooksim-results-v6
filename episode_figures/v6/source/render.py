"""Re-render reviewed geometry; outputs never overwrite shared native masters."""
from pathlib import Path
import argparse,json
from vector5 import WideFigure

def render(path):
    cfg=json.loads(path.read_text());c=WideFigure(cfg['name'],cfg['height'],cfg['title'],cfg['width'])
    scopes=[];previous=[]
    for r in cfg['elements']:
        names=r['group'].split('/') if r['group'] else []
        common=0
        while common<min(len(names),len(previous)) and names[common]==previous[common]:common+=1
        while len(scopes)>common:scopes.pop().__exit__(None,None,None)
        for name in names[common:]:
            ctx=c.group(name);ctx.__enter__();scopes.append(ctx)
        previous=names
        kind=r['kind']
        if kind=='text':c.text(r['x'],r['y'],r['text'],r['size'],r['weight'],r['anchor'],r['color'],r['family'],r.get('italic',False))
        elif kind=='rect':c.rect(r['x'],r['y'],r['w'],r['h'],r['fill'],r['stroke'],r.get('radius',0),r['sw'])
        elif kind=='ellipse':
            assert r['w']==r['h'];c.circle(r['x']+r['w']/2,r['y']+r['h']/2,r['w']/2,r['fill'],r['stroke'],r['sw'])
        elif kind=='edge':c.path(r['points'],r['color'],r['sw'],r['arrow'],r['dash'])
        elif kind=='image':c.photo(r['x'],r['y'],r['w'],r['h'],r['source'],r['crop'],border=None,rounded=r.get('clip_radius',0))
        else:raise ValueError(kind)
    while scopes:scopes.pop().__exit__(None,None,None)
    c.save()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('figures',nargs='+',type=Path);a=p.parse_args()
    for path in a.figures:render(path)
