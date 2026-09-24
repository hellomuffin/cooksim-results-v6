#!/usr/bin/env python3
"""Vector scatter plots of the exact scores used in the result tables."""
from pathlib import Path
import csv
import json
import math
import random
import zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from build_engine_tables import ENGINES, GROUPS, tag_for

HERE = Path(__file__).resolve().parent
COLORS = ['#287575','#466BAB','#AD702B','#8A5BA2']
MARKERS = ['o','D','s','^']
FAMILIES = ['Frontier API','Streaming API','Open-weight non-streaming','Open-weight streaming']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,
    'axes.labelsize':8.5,'xtick.labelsize':7.5,'ytick.labelsize':7.5,
    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','axes.linewidth':.65})


def records():
    engines={e:json.loads((HERE/f'{e}_metrics.json').read_text())['models'] for e,_ in ENGINES}
    rows=[]
    for g,(_,models) in enumerate(GROUPS):
        for tag,label in models:
            per=[]
            for e,_ in ENGINES:
                d=engines[e][tag_for(e,tag)]
                row=dict(engine=e,model=label,family=g,success=100*d['success'],quality=100*d['quality']['overall'])
                rows.append(row)
                per.append(row)
            rows.append(dict(engine='overall',model=label,family=g,
                             success=sum(r['success'] for r in per)/3,
                             quality=sum(r['quality'] for r in per)/3))
    return rows


def labels(ax, rows):
    """Deterministic label placement; data points are never moved or jittered."""
    fig=ax.figure
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    bounds=ax.get_window_extent().padded(-4)
    points=[ax.transData.transform((r['success'],r['quality'])) for r in rows]
    obstacles=[Bbox.from_bounds(x-5,y-5,10,10) for x,y in points]
    sizes=[]
    for r in rows:
        t=ax.text(0,0,r['model'],fontsize=7.1)
        b=t.get_window_extent(renderer)
        sizes.append((b.width+4,b.height+3))
        t.remove()
    best=None
    for seed in range(80):
        rng=random.Random(seed)
        order=sorted(range(len(rows)),key=lambda i:-rows[i]['quality'])
        if seed:
            rng.shuffle(order)
        placed=[]
        cost=0
        result={}
        for i in order:
            px,py=points[i]; w,h=sizes[i]
            options=[]
            for gap in [7,12,20,29,41,56,75]:
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
                    cx=px+dx*(w/2+gap); cy=py+dy*(h/2+gap)
                    box=Bbox.from_bounds(cx-w/2,cy-h/2,w,h)
                    if box.x0<bounds.x0 or box.x1>bounds.x1 or box.y0<bounds.y0 or box.y1>bounds.y1:
                        continue
                    overlaps=sum(box.overlaps(b) for b in placed+obstacles)
                    distance=math.hypot(max(abs(cx-px)-w/2,0),max(abs(cy-py)-h/2,0))
                    options.append((overlaps*10000+distance+(0 if dy>=0 else 2),cx,cy,box))
            choice=min(options,key=lambda x:x[0])
            cost+=choice[0]
            placed.append(choice[3]);result[i]=choice
        if best is None or cost<best[0]:best=(cost,result)
    assert best[0]<10000, 'Label collision; enlarge canvas or revise placement.'
    for i,r in enumerate(rows):
        _,cx,cy,box=best[1][i]
        xy=ax.transData.inverted().transform((cx,cy))
        px,py=points[i]
        distance=math.hypot(max(abs(cx-px)-box.width/2,0),max(abs(cy-py)-box.height/2,0))
        ax.annotate(r['model'],(r['success'],r['quality']),xytext=xy,
                    ha='center',va='center',fontsize=7.1,color=COLORS[r['family']],zorder=5,
                    bbox=dict(facecolor='white',edgecolor='none',alpha=.9,pad=.5),
                    arrowprops=dict(arrowstyle='-',color=COLORS[r['family']],lw=.45,alpha=.6,
                                    shrinkA=2,shrinkB=5) if distance>10 else None)


def plot(key,title,rows):
    fig=plt.figure(figsize=(5.5,4.05),dpi=150,facecolor='white')
    ax=fig.add_axes([.13,.23,.835,.665])
    x_max=math.ceil((max(r['success'] for r in rows)+8)/10)*10
    y_max=math.ceil((max(r['quality'] for r in rows)+8)/10)*10
    ax.set(xlim=(-x_max*.025,x_max),ylim=(0,y_max),
           xlabel='In-time task success rate (%)',ylabel='Interaction quality (%)')
    ax.set_xticks(range(0,x_max+1,10 if x_max<=60 else 20))
    ax.set_yticks(range(0,y_max+1,10 if y_max<=70 else 20))
    ax.set_title(title,loc='left',fontsize=9.2,fontweight='semibold',pad=11,color='#263E49')
    ax.grid(color='#E4E8EB',linewidth=.5,zorder=0)
    ax.tick_params(length=2.5,width=.6,color='#6A7780',labelcolor='#40525D')
    for spine in ax.spines.values():spine.set_color('#A6B1B8')
    for r in rows:
        ax.scatter(r['success'],r['quality'],s=34,marker=MARKERS[r['family']],
                   facecolor=COLORS[r['family']],edgecolor='white',linewidth=.6,zorder=4)
    labels(ax,rows)
    handles=[Line2D([],[],marker=m,color='none',markerfacecolor=c,markeredgecolor='white',
                    markersize=6,label=n) for c,m,n in zip(COLORS,MARKERS,FAMILIES)]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.55,.015),ncol=2,
               frameon=False,fontsize=7.1,columnspacing=1.8,handletextpad=.45,labelspacing=.7)
    name='success_quality_'+key
    for ext in ['pdf','svg','png']:
        fig.savefig(HERE/f'{name}.{ext}',dpi=240,metadata={'Creator':'Interactive Visual Gym'})
    plt.close(fig)
    print(f'{name}: {len(rows)} models; collision-free labels; editable SVG and vector PDF')


def main():
    rows=records()
    for key,title in [('overall','Across environments · equal-weight mean')]+ENGINES:
        plot(key,title,[r for r in rows if r['engine']==key])
    with (HERE/'success_quality_data.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['engine','model','family','success','quality'])
        w.writeheader();w.writerows(rows)
    with zipfile.ZipFile(HERE/'success_quality_sources.zip','w',zipfile.ZIP_DEFLATED) as z:
        for pattern in ['success_quality_*.svg','success_quality_*.pdf','*_metrics.json']:
            for path in HERE.glob(pattern):z.write(path,path.name)
        for name in ['success_quality_data.csv','build_success_quality.py','build_engine_tables.py','table_render.py']:
            z.write(HERE/name,name)


if __name__=='__main__':main()
