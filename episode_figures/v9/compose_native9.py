"""Narrow only the world panel; translate the remaining actors without reflow."""
from copy import deepcopy
from xml.etree import ElementTree as ET
import json,re
from compose_native8 import ROOT,GALLERY,OUT,FONTS,export

def build():
    overview=ET.parse(GALLERY/'episode_figures/v8/overview_matched.drawio')
    original=deepcopy(overview)
    conversation=ET.parse(GALLERY/'episode_figures/v6/interaction_episodes.drawio')
    cells={c.get('id'):c for c in overview.findall('.//mxCell')}
    def geo(id,**attrs):
        g=cells[str(id)].find('mxGeometry')
        for k,v in attrs.items():g.set(k,str(v))
    def text(id,value,x,y,w,h,size=None):
        c=cells[str(id)];c.set('value',value);geo(id,x=x,y=y,width=w,height=h)
        if size:c.set('style',re.sub(r'fontSize=[^;]+',f'fontSize={size}',c.get('style')))
    def divider(id,y1,y2):
        g=cells[str(id)].find('mxGeometry')
        for p,y in zip(g.findall('mxPoint'),[y1,y2]):p.set('x','112');p.set('y',str(y))
    delta=290
    for id in ['component-0','2','3','4']:geo(id,width=450)
    text(5,'World Engine',114.25,16.88,221.5,46.8)
    # Same three rows, compact content; no stretched or squeezed imagery.
    geo(6,x=20,y=88,width=410,height=154);divider(7,89,241)
    text(8,'Task',35.7,146.8,60.64,36.4)
    text(9,'Make a\ncheeseburger',130,96,284,78,32)
    text(10,'Bun, cooked patty,\nthen cheese.',130,178,284,56,24)
    geo(11,x=20,y=260,width=410,height=170);divider(12,261,429)
    text(13,'Render',24.3,326.8,87.38,36.4,26)
    text(14,'Top-down',128,272,142,32.5,24)
    text(15,'Egocentric',280,272,142,32.5,24)
    geo(16,x=128,y=310,width=142,height=106.5)
    geo(17,x=280,y=310,width=142,height=106.5)
    geo(18,x=20,y=448,width=410,height=146);divider(19,449,593)
    text(20,'Action',24.7,483,84.58,36.4,26)
    text(21,'space',28.4,522,77.27,36.4,26)
    geo(22,x=128,y=462,width=294,height=70)
    text(23,'go to the bottom\nleft pan',144,465,260,64,24)
    geo(24,x=128,y=544,width=160,height=38)
    text(25,'turn on',157,547,102,31.2,24)
    geo(26,x=300,y=544,width=48,height=38)
    text(27,'...',314,547,20.58,31.2,24)
    for id in ['component-1','component-2','component-3','component-4','component-5']:
        g=cells[id].find('mxGeometry');g.set('x',str(float(g.get('x'))-delta))
    overview.find('.//mxGraphModel').set('pageWidth','1290')
    # Wording is preserved modulo whitespace; all non-world child geometry intact.
    for old in original.findall('.//mxCell'):
        new=cells[old.get('id')]
        assert ' '.join(old.get('value','').split())==' '.join(new.get('value','').split())
        if old.get('parent') not in ['1','component-0']:
            assert ET.tostring(old)==ET.tostring(new)
    ET.indent(overview);overview.write(OUT/'overview_matched_v9.drawio',encoding='utf-8',xml_declaration=True)
    height=1930.;scale=height/614.;gap=180.;lw=1264*scale;rw=3536.;total=lw+gap+rw
    root=ET.Element('mxfile',host='app.diagrams.net')
    dia=ET.SubElement(root,'diagram',name='Balanced overview and conversation',id='overview_dialogue_v9')
    model=ET.SubElement(dia,'mxGraphModel',dx='0',dy='0',grid='0',page='1',pageScale='1',pageWidth=str(total),pageHeight=str(height),math='0',shadow='0',extFonts=FONTS)
    dest=ET.SubElement(model,'root');ET.SubElement(dest,'mxCell',id='0');ET.SubElement(dest,'mxCell',id='1',parent='0')
    for prefix,doc,sc,bounds,offset in [('overview',overview,scale,(14,12,1264,614),0),('conversation',conversation,1,(32,14,3536,1930),lw+gap)]:
        grp=ET.SubElement(dest,'mxCell',id=prefix,parent='1',vertex='1',connectable='0',style='group;')
        ET.SubElement(grp,'mxGeometry',x=str(offset),y='0',width=str(bounds[2]*sc),height=str(height),attrib={'as':'geometry'})
        for source in doc.findall('.//mxGraphModel/root/mxCell'):
            if source.get('id') in ('0','1'):continue
            cell=deepcopy(source);cell.set('id',prefix+'-'+cell.get('id'))
            parent=cell.get('parent');cell.set('parent',prefix if parent=='1' else prefix+'-'+parent)
            for key in ('source','target'):
                if cell.get(key):cell.set(key,prefix+'-'+cell.get(key))
            g=cell.find('mxGeometry')
            if g is not None:
                for e in g.iter():
                    for k in ('x','y','width','height'):
                        if e.get(k) is not None:e.set(k,str(float(e.get(k))*sc))
                if parent=='1':
                    g.set('x',str(float(g.get('x','0'))-bounds[0]*sc))
                    g.set('y',str(float(g.get('y','0'))-bounds[1]*sc))
            cell.set('style',re.sub(r'\b(fontSize|strokeWidth|arcSize|endSize|startSize)=([0-9.]+)',lambda m:m[1]+'='+str(float(m[2])*sc),cell.get('style','')))
            dest.append(cell)
    ET.indent(root);ET.ElementTree(root).write(OUT/'overview_dialogue_v9.drawio',encoding='utf-8',xml_declaration=True)
    audit=dict(world_panel_width_before=740,world_panel_width_after=450,overview_fraction=lw/(lw+rw),conversation_fraction=rw/(lw+rw),equal_height=height,overview_scale=scale,conversation_scale=1,other_actors_translation_x=-delta,other_actors_geometry_unchanged=True,wording_unchanged_except_linebreaks=True,world_image_scale=142/264,gap=gap)
    (ROOT/'audits/revision9_composition.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit),flush=True)

if __name__=='__main__':build();export(['overview_dialogue_v9','overview_matched_v9'])
