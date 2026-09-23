"""Restyle and proportionally align existing native drawings. No layout reflow."""
from pathlib import Path
from copy import deepcopy
from xml.etree import ElementTree as ET
import base64,json,re,subprocess
from playwright.sync_api import sync_playwright
from sample_engines import CHROME
ROOT=Path(__file__).resolve().parent
GALLERY=ROOT.parents[2]/'cooksim-results-v6'
OUT=ROOT/'out'
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS);ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
COLORS={'#28786F':'#85573F','#555D8C':'#405F7B','#30464B':'#293C49','#202C35':'#293C49',
 '#607378':'#586973','#826B45':'#85573F','#EAF4EF':'#F7F0E9','#D6E8DF':'#E9D9CA',
 '#F8FCFA':'#FFFFFF','#E7E8F2':'#EFF3F7','#E3E5F2':'#EFF3F7','#F7F7FB':'#FFFFFF',
 '#C5C8DA':'#B1BFC6','#C8D4D5':'#B1BFC6','#F5F7F7':'#FFFFFF','#E7EDEE':'#EFF3F7',
 '#FFFAF1':'#F7F0E9','#FFF9EF':'#F7F0E9','#DDCEB3':'#B1BFC6','#E0D3BA':'#B1BFC6',
 '#EDF5F2':'#F7F0E9','#B8CDC5':'#B1BFC6','#BBCEC9':'#B1BFC6','#9BBFB1':'#B1BFC6'}
FONTS='Manrope^https://hellomuffin.github.io/cooksim-results-v6/episode_figures/v5/fonts/Manrope-Regular.ttf|Manrope SemiBold^https://hellomuffin.github.io/cooksim-results-v6/episode_figures/v5/fonts/Manrope-SemiBold.ttf'

def build():
    overview=ET.parse(GALLERY/'figure1/figure1_a_four_rows.drawio')
    conversation=ET.parse(GALLERY/'episode_figures/v6/interaction_episodes.drawio')
    original=deepcopy(overview)
    for c in overview.findall('.//mxCell'):
        st=c.get('style','')
        for old,new in COLORS.items():st=st.replace(old,new)
        if 'fontFamily=' in st:
            fam='Manrope SemiBold' if ('SemiBold' in st or 'Serif' in st) else 'Manrope'
            st=re.sub(r'fontFamily=[^;]+',f'fontFamily={fam}',st)
        c.set('style',st)
    # Wording and every coordinate are unchanged by styling.
    for before,after in zip(original.findall('.//mxCell'),overview.findall('.//mxCell')):
        assert before.get('value')==after.get('value')
        bg=before.find('mxGeometry');ag=after.find('mxGeometry')
        assert (ET.tostring(bg) if bg is not None else None)==(ET.tostring(ag) if ag is not None else None)
    overview.find('.//mxGraphModel').set('extFonts',FONTS)
    overview.write(OUT/'overview_matched_v8.drawio',encoding='utf-8',xml_declaration=True)

    height=1930.;scale=height/614.;gap=180.;lw=1554*scale;rw=3536.;total=lw+gap+rw
    root=ET.Element('mxfile',host='app.diagrams.net')
    dia=ET.SubElement(root,'diagram',name='Overview and conversation · unchanged layouts',id='overview_dialogue_v8')
    model=ET.SubElement(dia,'mxGraphModel',dx='0',dy='0',grid='0',page='1',pageScale='1',pageWidth=str(total),pageHeight=str(height),math='0',shadow='0',extFonts=FONTS)
    cells=ET.SubElement(model,'root');ET.SubElement(cells,'mxCell',id='0');ET.SubElement(cells,'mxCell',id='1',parent='0')
    for prefix,doc,sc,bounds,offset in [('overview',overview,scale,(14,12,1554,614),0),('conversation',conversation,1,(32,14,3536,1930),lw+gap)]:
        grp=ET.SubElement(cells,'mxCell',id=prefix,parent='1',vertex='1',connectable='0',style='group;')
        ET.SubElement(grp,'mxGeometry',x=str(offset),y='0',width=str(bounds[2]*sc),height=str(height),attrib={'as':'geometry'})
        for source in doc.findall('.//mxGraphModel/root/mxCell'):
            if source.get('id') in ('0','1'):continue
            cell=deepcopy(source);cell.set('id',prefix+'-'+cell.get('id'))
            parent=cell.get('parent');cell.set('parent',prefix if parent=='1' else prefix+'-'+parent)
            for key in ('source','target'):
                if cell.get(key):cell.set(key,prefix+'-'+cell.get(key))
            geo=cell.find('mxGeometry')
            if geo is not None:
                for e in geo.iter():
                    for k in ('x','y','width','height'):
                        if e.get(k) is not None:e.set(k,str(float(e.get(k))*sc))
                if parent=='1':
                    geo.set('x',str(float(geo.get('x','0'))-bounds[0]*sc))
                    geo.set('y',str(float(geo.get('y','0'))-bounds[1]*sc))
            cell.set('style',re.sub(r'\b(fontSize|strokeWidth|arcSize|endSize|startSize)=([0-9.]+)',lambda m:m[1]+'='+str(float(m[2])*sc),cell.get('style','')))
            cells.append(cell)
    ET.indent(root);ET.ElementTree(root).write(OUT/'overview_dialogue_v8.drawio',encoding='utf-8',xml_declaration=True)
    (ROOT/'audits/revision8_composition.json').write_text(json.dumps(dict(layout_changed=False,wording_changed=False,overview_scale=scale,conversation_scale=1,matched_height=height,gap=gap,canvas_width=total,native_output_width_pt=total*.11,native_output_height_pt=height*.11,overview_source='figure1/figure1_a_four_rows.drawio',conversation_source='episode_figures/v6/interaction_episodes.drawio'),indent=2))

def export():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1700,'height':950})
        page.set_content('<iframe id="editor" src="https://embed.diagrams.net/?embed=1&proto=json&spin=1" style="width:98vw;height:95vh;border:0"></iframe><script>window.msgs=[];window.addEventListener("message",e=>{try{msgs.push(JSON.parse(e.data));}catch{}})</script>')
        page.wait_for_function('msgs.some(e=>e.event==="init")',timeout=60000)
        for name in ['overview_dialogue_v8','overview_matched_v8']:
            native=ET.parse(OUT/f'{name}.drawio')
            page.evaluate('window.msgs=[]')
            page.evaluate('(xml)=>document.getElementById("editor").contentWindow.postMessage(JSON.stringify({action:"load",xml,fit:1}),"*")',(OUT/f'{name}.drawio').read_text())
            page.wait_for_function('msgs.some(e=>e.event==="load")',timeout=60000)
            frame=page.frames[1];frame.evaluate('document.fonts.ready');frame.wait_for_timeout(1500)
            page.screenshot(path=str(ROOT/'audits'/f'{name}_native.png'))
            page.evaluate('()=>document.getElementById("editor").contentWindow.postMessage(JSON.stringify({action:"export",format:"svg",embedImages:true,background:"#ffffff",border:0}),"*")')
            page.wait_for_function('msgs.some(e=>e.event==="export")',timeout=60000)
            data=page.evaluate('msgs.find(e=>e.event==="export")')
            svg=ET.fromstring(base64.b64decode(data['data'].split(',',1)[1]))
            sources={}
            for cell in native.findall('.//mxCell'):
                style=cell.get('style','')
                if 'image=data:image/svg+xml,' in style:sources[cell.get('id')]=ET.fromstring(base64.b64decode(style.split('image=data:image/svg+xml,',1)[1].split(';',1)[0]))
            images=list(svg.iter('{'+NS+'}image'));parents={child:parent for parent in svg.iter() for child in parent}
            assert len(images)==len(sources),(len(images),len(sources))
            for i,im in enumerate(images):
                ancestor=im
                while ancestor.get('data-cell-id') not in sources:ancestor=parents[ancestor]
                source=sources[ancestor.get('data-cell-id')]
                ids={e.get('id'):f'camera-{i}-'+e.get('id') for e in source.iter() if e.get('id')}
                for e in source.iter():
                    for key,value in list(e.attrib.items()):
                        if key=='id':e.set(key,ids[value])
                        else:
                            for old,new in ids.items():value=value.replace('url(#'+old+')','url(#'+new+')')
                            e.set(key,value)
                for key in ('x','y','width','height','transform'):
                    if im.get(key):source.set(key,im.get(key))
                source.set('overflow','hidden')
                parent=parents[im];idx=list(parent).index(im);parent.remove(im)
                defs=ET.Element('{'+NS+'}defs');clip=ET.SubElement(defs,'{'+NS+'}clipPath',id=f'camera-{i}',clipPathUnits='userSpaceOnUse')
                ET.SubElement(clip,'{'+NS+'}rect',**{key:im.get(key,'0') for key in ('x','y','width','height')})
                group=ET.Element('{'+NS+'}g',{'clip-path':f'url(#camera-{i})'});group.append(source)
                parent.insert(idx,defs);parent.insert(idx+1,group)
            for e in svg.iter():
                if 'style' in e.attrib:e.set('style',';'.join(s for s in e.get('style').split(';') if s.strip() and 'light-dark(' not in s))
            css=[]
            for fam,file in [('Manrope','Manrope-Regular.ttf'),('Manrope SemiBold','Manrope-SemiBold.ttf')]:
                b64=base64.b64encode((ROOT/'assets/manrope'/file).read_bytes()).decode()
                css.append('@font-face{font-family:"'+fam+'";src:url(data:font/ttf;base64,'+b64+') format("truetype");}')
            defs=ET.Element('{'+NS+'}defs');ET.SubElement(defs,'{'+NS+'}style').text=''.join(css);svg.insert(0,defs)
            vb=list(map(float,svg.get('viewBox').split()))
            outw=vb[2]*(.11 if name=='overview_dialogue_v8' else 396/vb[2])
            svg.set('width',f'{outw}pt');svg.set('height',f'{outw*vb[3]/vb[2]}pt')
            svg.set('style','background:white;color-scheme:light')
            ET.SubElement(svg,'{'+NS+'}title').text='Existing overview and conversation, uniformly styled and proportionally scaled' if name=='overview_dialogue_v8' else 'Overview with matched visual styling'
            ET.ElementTree(svg).write(OUT/f'{name}.svg',encoding='utf-8',xml_declaration=True)
            for fmt in ('pdf','png'):
                cmd=['inkscape',str(OUT/f'{name}.svg'),f'--export-type={fmt}',f'--export-filename={OUT/name}.{fmt}']
                if fmt=='png':cmd.append('--export-dpi=144')
                subprocess.run(cmd,check=True,capture_output=True)
            print(name,'rendered',outw,'pt',flush=True)
        browser.close()

if __name__=='__main__':build();export()
