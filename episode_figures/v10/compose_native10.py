"""Latest author wording; horizontal actor cards with assistant below human."""
from copy import deepcopy
from xml.etree import ElementTree as ET
import hashlib,json,re
from compose_native8 import ROOT,GALLERY,OUT,FONTS,export
from vector import wrap,width

SOURCE=GALLERY/'episode_figures/v9/overview_dialogue.drawio'
OV_SCALE=1930/614
ARROW_FONT=62*840/1930

def transform(cell,scale=1,dx=0,dy=0):
    g=cell.find('mxGeometry')
    if g is not None:
        for e in g.iter():
            for k in ('x','y','width','height'):
                if e.get(k) is not None:e.set(k,str(float(e.get(k))*scale))
        if cell.get('edge')=='1':
            for p in g.iter('mxPoint'):
                p.set('x',str(float(p.get('x','0'))+dx));p.set('y',str(float(p.get('y','0'))+dy))
        else:
            g.set('x',str(float(g.get('x','0'))+dx));g.set('y',str(float(g.get('y','0'))+dy))
    cell.set('style',re.sub(r'\b(fontSize|strokeWidth|arcSize|endSize|startSize)=([0-9.]+)',lambda m:m[1]+'='+str(float(m[2])*scale),cell.get('style','')))

def extract(source,prefix,scale=1):
    root=ET.Element('mxfile',host='app.diagrams.net')
    d=ET.SubElement(root,'diagram',name=prefix,id=prefix)
    model=ET.SubElement(d,'mxGraphModel',grid='0',page='1',pageWidth='1140',pageHeight='880',extFonts=FONTS)
    dst=ET.SubElement(model,'root');ET.SubElement(dst,'mxCell',id='0');ET.SubElement(dst,'mxCell',id='1',parent='0')
    allcells={c.get('id'):c for c in source.findall('.//mxCell')}
    def belongs(c):
        p=c.get('parent')
        while p in allcells and p not in ['0','1',prefix]:p=allcells[p].get('parent')
        return p==prefix
    selected=[c for c in allcells.values() if belongs(c)]
    ids={c.get('id'):(c.get('id')[len(prefix)+1:] if c.get('id').startswith(prefix+'-') else c.get('id')) for c in selected}
    for old in selected:
        id=old.get('id','')
        c=deepcopy(old);c.set('id',ids[id])
        parent=c.get('parent');c.set('parent','1' if parent==prefix else ids[parent])
        for key in ('source','target'):
            if c.get(key):c.set(key,ids[c.get(key)])
        transform(c,scale);dst.append(c)
    return ET.ElementTree(root)

def clean_dialogue(doc):
    """Rewrap the author's shorter turns without replacing their wording."""
    root=doc.find('.//mxGraphModel/root');cells={c.get('id'):c for c in root.findall('mxCell')}
    removed_loops=[]
    for c in list(root):
        if c.get('edge')=='1' and c.get('source') and c.get('source')==c.get('target'):
            removed_loops.append(c.get('id'));root.remove(c)
    changes=[]
    for ids,bubble in [([str(i) for i in range(35,41)],'34'),(['46','47'],'45'),(['65','66'],'64')]:
        ids=[id for id in ids if id in cells]
        text=' '.join(' '.join(cells[id].get('value','').split()) for id in ids)
        g=cells[ids[0]].find('mxGeometry');bg=cells[bubble].find('mxGeometry')
        font=float(re.search(r'fontSize=([0-9.]+)',cells[ids[0]].get('style'))[1])
        lines=wrap(text,float(bg.get('width'))-48,font,'Manrope')
        assert len(lines)<=len(ids)
        x=float(g.get('x'));y=float(g.get('y'));oldh=float(bg.get('height'))
        for i,id in enumerate(ids):
            if i>=len(lines):root.remove(cells[id]);continue
            c=cells[id];c.set('value',lines[i]);cg=c.find('mxGeometry')
            cg.set('x',str(x));cg.set('y',str(y+i*font*1.3));cg.set('width',str(width(lines[i],font,'Manrope')+.5));cg.set('height',str(font*1.3))
        if bubble in ['34','45']:
            newh=len(lines)*font*1.3+36;bg.set('height',str(newh));delta=newh-oldh
            moving=range(41,54) if bubble=='34' else range(49,54)
            for id in map(str,moving):
                if id in cells and cells[id] in list(root):transform(cells[id],1,0,delta)
        changes.append(dict(bubble=bubble,author_text=text,lines=lines))
    # Fit the shorter A episode to its last observation rather than retain an
    # empty tail inside its frame. The branch structure and content are unchanged.
    last=cells['53'].find('mxGeometry')
    ah=float(last.get('y'))+float(last.get('height'))+42
    cells['22'].find('mxGeometry').set('height',str(ah))
    for p in cells['25'].find('mxGeometry').findall('mxPoint'):
        if p.get('as')=='targetPoint':p.set('y',str(ah-38))
    # The author renamed this caption; keep it within the timeline's right edge.
    timestamp=cells['11'];tg=timestamp.find('mxGeometry')
    tf=float(re.search(r'fontSize=([0-9.]+)',timestamp.get('style'))[1])
    tw=width(timestamp.get('value'),tf,'Manrope')+.5
    tg.set('x',str(3504-tw));tg.set('width',str(tw))
    return dict(reflowed_turns=changes,removed_empty_self_loop_connectors=removed_loops,assistant_a_frame_height=ah)

def build():
    latest=ET.parse(SOURCE)
    overview=extract(latest,'overview',1/OV_SCALE)
    conversation=extract(latest,'conversation')
    original=deepcopy(overview)
    cells={c.get('id'):c for c in overview.findall('.//mxCell')}
    def geo(id,**attrs):
        g=cells[str(id)].find('mxGeometry')
        for k,v in attrs.items():g.set(k,str(v))
    def style(id,**attrs):
        c=cells[str(id)];s=c.get('style','')
        for key,value in attrs.items():
            s=re.sub(r'\b'+key+r'=[^;]*',key+'='+str(value),s) if key+'=' in s else s+key+'='+str(value)+';'
        c.set('style',s)
    def text(id,x,y,w,h,size=None,value=None,align=None):
        geo(id,x=x,y=y,width=w,height=h)
        if value is not None:cells[str(id)].set('value',value)
        if size is not None:style(id,fontSize=size)
        if align:style(id,align=align)
    def edge(id,points):
        cell=cells[str(id)];old=cell.find('mxGeometry');cell.remove(old)
        g=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
        for label,p in [('sourcePoint',points[0]),('targetPoint',points[-1])]:
            ET.SubElement(g,'mxPoint',x=str(p[0]),y=str(p[1]),attrib={'as':label})
        if len(points)>2:
            a=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in points[1:-1]:ET.SubElement(a,'mxPoint',x=str(x),y=str(y))
    # World content: preserve the author's two task lines and single-line action.
    geo('component-0',x=16,y=90,width=520,height=614)
    for id in [2,3,4]:geo(id,width=520)
    text(5,125,16.88,270,46.8,34)
    geo(6,x=20,y=88,width=480,height=112);edge(7,[(112,89),(112,199)])
    text(8,35,126,62,36.4,27)
    text(9,132,103,354,82,30,value=cells['9'].get('value').replace('\xa0',' '))
    geo(11,x=20,y=218,width=480,height=218);edge(12,[(112,219),(112,435)])
    text(13,23,310,88,36.4,26)
    # The author removed top-down/egocentric labels in the latest save.
    if '14' in cells:text(14,132,240,164,32.5,24)
    if '15' in cells:text(15,318,240,164,32.5,24)
    geo(16,x=132,y=265,width=164,height=123);geo(17,x=318,y=265,width=164,height=123)
    geo(18,x=20,y=454,width=480,height=140);edge(19,[(112,455),(112,593)])
    text(20,24,480,86,36.4,26);text(21,28,519,78,36.4,26)
    geo(22,x=132,y=470,width=350,height=50)
    text(23,144,477,326,35,26)
    geo(24,x=132,y=534,width=144,height=42);text(25,153,539,102,31.2,25)
    geo(26,x=292,y=534,width=48,height=42);text(27,306,539,21,31.2,25)
    # Two compact conditioning cards remain above the simulated human.
    geo('component-1',x=602,y=20,width=512,height=270)
    geo(28,x=0,y=0,width=214,height=190);geo(33,x=232,y=0,width=280,height=190)
    text(29,19,13,180,37,28);text(30,19,62,183,35,26)
    text(31,19,102,183,35,26);text(32,19,142,183,35,26)
    text(34,251,13,244,37,28);text(36,251,62,244,35,26)
    text(37,251,102,244,35,26);text('XBWEUn51nucrvOGzJZNo-73',251,142,244,35,26)
    edge(38,[(107,192),(107,221),(372,221),(372,192)])
    edge(39,[(315,221),(315,261)])
    # Human: title/self-planning on the left, original human stencil on the right.
    geo('component-3',x=720,y=290,width=394,height=220)
    geo(54,x=0,y=0,width=394,height=220)
    geo(55,x=0,y=0,width=240,height=220)
    geo(56,x=220,y=0,width=20,height=220)
    text(57,21,55,211,45,34,align='left');text(58,21,108,211,45,34,align='left')
    for id in [59,60]:transform(cells[str(id)],1.2,250-76*1.2,48-144*1.2)
    if '63' in cells:geo(63,x=16,y=155,width=208,height=45)
    if '64' in cells:text(64,23,160,194,35,25,align='center')
    # Assistant: same left-label/right-icon grammar; original robot preserved.
    geo('component-2',x=720,y=675,width=394,height=185)
    geo(40,x=0,y=0,width=394,height=185)
    geo(41,x=0,y=0,width=240,height=185)
    geo(42,x=220,y=0,width=20,height=185)
    text(43,21,40,211,45,34,align='left');text(44,21,90,211,45,34,align='left')
    for id in range(45,54):transform(cells[str(id)],.86,259-16*.86,16-123.8*.86)
    # User–world interface remains horizontal and is the only action interface.
    geo('component-5',x=548,y=311,width=160,height=178)
    edge(70,[(160,52),(0,52)]);edge(72,[(0,122),(160,122)])
    text(71,-1,6,162,35,ARROW_FONT,align='center')
    text(73,-6,133,172,35,ARROW_FONT,align='center')
    # User observations/messages go down; assistant guidance returns upward.
    geo('component-4',x=720,y=521,width=394,height=143)
    edge(67,[(42,0),(42,143)]);edge(65,[(352,143),(352,0)])
    text(68,66,22,189,35,ARROW_FONT,align='left')
    text(69,66,58,160,35,ARROW_FONT,align='left')
    text(66,211,92,134,35,ARROW_FONT,align='left')
    # All author wording survives; conversation source is the edited composite.
    for old in original.findall('.//mxCell'):
        assert ' '.join(old.get('value','').split())==' '.join(cells[old.get('id')].get('value','').split()),old.get('id')
    ET.indent(overview);overview.write(OUT/'overview_matched_v10.drawio',encoding='utf-8',xml_declaration=True)
    conversation_audit=clean_dialogue(conversation)
    ET.indent(conversation);conversation.write(OUT/'conversation_preserved_v10.drawio',encoding='utf-8',xml_declaration=True)
    # Uniform composition transforms: original conversation font = 62 native units.
    height=1930.;sc=height/840.;lw=1098*sc;rw=3536.;gap=55*sc
    root=ET.Element('mxfile',host='app.diagrams.net')
    dia=ET.SubElement(root,'diagram',name='Stacked actor cards and readable conversation',id='overview_dialogue_v10')
    model=ET.SubElement(dia,'mxGraphModel',dx='0',dy='0',grid='0',page='1',pageScale='1',pageWidth=str(lw+gap+rw),pageHeight=str(height),math='0',shadow='0',extFonts=FONTS)
    dst=ET.SubElement(model,'root');ET.SubElement(dst,'mxCell',id='0');ET.SubElement(dst,'mxCell',id='1',parent='0')
    for prefix,doc,scale,bounds,offset in [('overview',overview,sc,(16,20,1098,840),0),('conversation',conversation,1,(0,0,3536,1930),lw+gap)]:
        g=ET.SubElement(dst,'mxCell',id=prefix,parent='1',vertex='1',connectable='0',style='group;')
        ET.SubElement(g,'mxGeometry',x=str(offset),y='0',width=str(bounds[2]*scale),height=str(height),attrib={'as':'geometry'})
        for old in doc.findall('.//mxGraphModel/root/mxCell'):
            if old.get('id') in ('0','1'):continue
            c=deepcopy(old);c.set('id',prefix+'-'+c.get('id'));parent=c.get('parent')
            c.set('parent',prefix if parent=='1' else prefix+'-'+parent)
            for key in ['source','target']:
                if c.get(key):c.set(key,prefix+'-'+c.get(key))
            transform(c,scale,-bounds[0]*scale if parent=='1' else 0,-bounds[1]*scale if parent=='1' else 0)
            dst.append(c)
    ET.indent(root);ET.ElementTree(root).write(OUT/'overview_dialogue_v10.drawio',encoding='utf-8',xml_declaration=True)
    audit=dict(source='episode_figures/v9/overview_dialogue.drawio',source_commit='42331b2',source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),author_wording_preserved=True,conversation_formatting=conversation_audit,overview_width=lw,conversation_width=rw,conversation_fraction=rw/(rw+lw),overview_scale=sc,matched_height=height,arrow_font_native=ARROW_FONT*sc,dialogue_font_native=62,old_overview_arrow_font_native=28*OV_SCALE,gap=gap)
    (ROOT/'audits/revision10_composition.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit),flush=True)

if __name__=='__main__':build();export(['overview_dialogue_v10','overview_matched_v10'])
