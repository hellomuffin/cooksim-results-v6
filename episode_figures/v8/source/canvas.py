from pathlib import Path
from xml.etree import ElementTree as ET
from html import escape
from contextlib import contextmanager
import base64
import json
import subprocess
ROOT=Path(__file__).resolve().parent/'rendered'
ASSETS=ROOT
INK='#263A43'
MUTED='#66767C'
BLUE='#506D9C'
TEAL='#347363'
AMBER='#866332'
LINE='#CBD6D8'
FONT='IBM Plex Sans'

class Canvas:
    def __init__(self, name, h, title):
        self.name, self.h, self.title = name, h, title
        self.parts, self.records, self.stack = [], [], []
        self.n = 0

    def uid(self, prefix='el'):
        self.n += 1
        return f'{prefix}-{self.n}'

    @contextmanager
    def group(self, name):
        ident = self.uid('group')
        self.parts.append(f'<g id="{ident}" inkscape:label="{escape(name)}"' + (' inkscape:groupmode="layer"' if not self.stack else '') + '>')
        self.stack.append(name)
        yield
        self.stack.pop()
        self.parts.append('</g>')

    def add(self, markup, **record):
        self.parts.append(markup)
        self.records.append(dict(record, group='/'.join(self.stack)))

    def rect(self, x, y, w, h, fill='white', stroke=LINE, radius=3, sw=.65):
        ident = self.uid()
        self.add(f'<rect id="{ident}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
                 kind='rect', x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, radius=radius, sw=sw)

    def circle(self, x, y, r, fill='white', stroke=LINE, sw=.7):
        ident = self.uid()
        self.add(f'<circle id="{ident}" cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
                 kind='ellipse', x=x-r, y=y-r, w=r*2, h=r*2, fill=fill, stroke=stroke, sw=sw)

    def text(self, x, y, text, size=8.5, weight=400, anchor='start', color=INK, family=None, italic=False):
        assert size >= 8, (text, size)
        for i, line in enumerate(text.split('\n')):
            yy = y + i * size * 1.2
            ident = self.uid('text')
            self.add(f'<text id="{ident}" x="{x}" y="{yy}" font-family="{family or FONT}" font-size="{size}" font-weight="{weight}" font-style="{"italic" if italic else "normal"}" text-anchor="{anchor}" fill="{color}">{escape(line)}</text>',
                     kind='text', x=x, y=yy, text=line, size=size, weight=weight, anchor=anchor, color=color, family=family or 'Arial', italic=italic)

    def path(self, points, color=INK, sw=.85, arrow=False, dash=False):
        ident = self.uid('edge')
        path = 'M' + ' L'.join(f'{x},{y}' for x,y in points)
        extra = ' stroke-dasharray="2.4 2"' if dash else ''
        if arrow:
            extra += f' marker-end="url(#arrow-{color[1:]})"'
        self.add(f'<path id="{ident}" d="{path}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{extra}/>',
                 kind='edge', points=points, color=color, sw=sw, arrow=arrow, dash=dash)

    def arrow(self, x1,y1,x2,y2,color=INK,sw=.9,dash=False):
        self.path([(x1,y1),(x2,y2)],color,sw,True,dash)

    def image(self, x,y,w,h,filename,crop):
        # Crop via a vector viewport; original pixels are neither retouched nor resampled.
        from PIL import Image
        p = ASSETS / filename
        iw,ih = Image.open(p).size
        mime = 'image/png' if p.suffix == '.png' else 'image/jpeg'
        data = base64.b64encode(p.read_bytes()).decode()
        cx,cy,cw,ch = crop
        snippet = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="{cx} {cy} {cw} {ch}" preserveAspectRatio="xMidYMid slice"><image width="{iw}" height="{ih}" xlink:href="data:{mime};base64,{data}"/></svg>'
        ident=self.uid('image')
        self.add(f'<defs><clipPath id="clip-{ident}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#clip-{ident})"><svg id="{ident}" x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{cx} {cy} {cw} {ch}" preserveAspectRatio="xMidYMid slice"><image width="{iw}" height="{ih}" xlink:href="data:{mime};base64,{data}"/></svg></g>',
                 kind='image',x=x,y=y,w=w,h=h,svg=snippet,source=filename,crop=crop)

    def save(self):
        width=getattr(self,'w',396)
        output_width=getattr(self,'output_width',width)
        output_height=self.h*output_width/width
        colors = [INK,MUTED,BLUE,TEAL,AMBER,LINE]
        markers=''.join(f'<marker id="arrow-{c[1:]}" viewBox="0 0 6 6" refX="5.3" refY="3" markerWidth="4.7" markerHeight="4.7" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L6,3 L0,6 Z" fill="{c}"/></marker>' for c in colors)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{output_width}pt" height="{output_height}pt" viewBox="0 0 {width} {self.h}"><title>{escape(self.title)}</title><desc>Editable figure at final ICLR width. Only the simulated user executes environment actions; the assistant communicates with the user.</desc><defs>{markers}</defs><rect id="page-background" width="{width}" height="{self.h}" fill="white"/>' + ''.join(self.parts) + '</svg>'
        path=ROOT/f'{self.name}.svg'
        changed=not path.exists() or path.read_text()!=svg
        path.write_text(svg)
        (ROOT/f'{self.name}.elements.json').write_text(json.dumps(self.records,indent=2))
        if changed or not (ROOT/f'{self.name}.pdf').exists():
            subprocess.run(['inkscape',str(path),'--export-type=pdf',f'--export-filename={ROOT/self.name}.pdf'],check=True,capture_output=True)
        if changed or not (ROOT/f'{self.name}.png').exists():
            subprocess.run(['inkscape',str(path),'--export-type=png','--export-dpi=216',f'--export-filename={ROOT/self.name}.png'],check=True,capture_output=True)
        self.drawio()

    def drawio(self):
        """Native text, shapes, and editable polyline arrows, not one embedded figure."""
        from PIL import ImageFont
        fonts={}
        for bold in (False,True):
            fontfile=subprocess.check_output(['fc-match','-f','%{file}',
                         'Arial:style='+('Bold' if bold else 'Regular')],text=True)
            fonts[bold]=ImageFont.truetype(fontfile,1024)
        mxfile=ET.Element('mxfile',host='app.diagrams.net')
        dia=ET.SubElement(mxfile,'diagram',name=self.title,id=self.name)
        model=ET.SubElement(dia,'mxGraphModel',dx='0',dy='0',grid='0',page='1',pageScale='1',pageWidth=str(getattr(self,'w',396)*2),pageHeight=str(self.h*2),math='0',shadow='0')
        root=ET.SubElement(model,'root'); ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
        def geometry(r):
            if r['kind']=='text':
                key=(r.get('family','Arial'),r['weight']>=600,r.get('italic',False))
                if key not in fonts:
                    style=('Bold ' if key[1] else '')+('Italic' if key[2] else 'Regular')
                    fontfile=subprocess.check_output(['fc-match','-f','%{file}',key[0]+':style='+style],text=True)
                    fonts[key]=ImageFont.truetype(fontfile,1024)
                w=max(8,fonts[key].getlength(r['text'])*r['size']/1024+.5)
                h=r['size']*1.3
                x=r['x']-({'start':0,'middle':w/2,'end':w}[r['anchor']])
                return x,r['y']-r['size']*.92,w,h
            if r['kind']=='edge':
                xs,ys=zip(*r['points'])
                return min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
            return tuple(r[z] for z in ('x','y','w','h'))
        # Logical groups let collaborators move a whole actor or engine panel.
        # Child labels remain native editable text.
        groups={}
        for r in self.records:
            group=r['group'].split('/')[0]
            if group:
                x,y,w,h=geometry(r)
                if group not in groups:groups[group]=[x,y,x+w,y+h]
                else:
                    b=groups[group]
                    groups[group]=[min(b[0],x),min(b[1],y),max(b[2],x+w),max(b[3],y+h)]
        group_ids={g:f'component-{i}' for i,g in enumerate(groups)}
        for g,(x,y,x2,y2) in groups.items():
            cell=ET.SubElement(root,'mxCell',id=group_ids[g],parent='1',vertex='1',style='group;',connectable='0')
            ET.SubElement(cell,'mxGeometry',x=str(x*2),y=str(y*2),width=str((x2-x)*2),height=str((y2-y)*2),attrib={'as':'geometry'})
        # Double coordinates for convenient online editing; proportions are identical.
        for i,r in enumerate(self.records,2):
            group=r['group'].split('/')[0]
            gx,gy=groups[group][:2] if group else (0,0)
            k=r['kind']; attrs={'id':str(i),'parent':group_ids.get(group,'1')}
            if k=='edge':
                attrs.update(edge='1',style=f'edgeStyle=none;rounded=0;html=0;strokeColor={r["color"]};strokeWidth={r["sw"]*2};endArrow={"block" if r["arrow"] else "none"};endSize=7;dashed={int(r["dash"])};')
                cell=ET.SubElement(root,'mxCell',attrs); geo=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
                pts=[(x-gx,y-gy) for x,y in r['points']];ET.SubElement(geo,'mxPoint',x=str(pts[0][0]*2),y=str(pts[0][1]*2),attrib={'as':'sourcePoint'});ET.SubElement(geo,'mxPoint',x=str(pts[-1][0]*2),y=str(pts[-1][1]*2),attrib={'as':'targetPoint'})
                if len(pts)>2:
                    arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
                    for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x*2),y=str(y*2))
                continue
            attrs['vertex']='1'
            if k=='text':
                # Real font metrics matter: overestimating a centered label's
                # width can put its editing box at x<0 and create a blank page.
                x,y,w,h=geometry(r)
                attrs.update(value=r['text'],style=f'text;html=0;whiteSpace=nowrap;overflow=visible;align={dict(start="left",middle="center",end="right")[r["anchor"]]};verticalAlign=middle;spacing=0;fontFamily={r.get("family","Arial")};fontSize={r["size"]*2};fontStyle={(1 if r["weight"]>=600 else 0)+(2 if r.get("italic",False) else 0)};fontColor={r["color"]};')
            elif k=='image':
                x,y,w,h=[r[z] for z in ('x','y','w','h')]
                encoded=base64.b64encode(r['svg'].encode()).decode()
                # mxGraph style values are semicolon-delimited. Its image loader
                # accepts base64 SVG after a comma; a literal ';base64' would
                # split the style and silently discard the picture.
                attrs['style']=f'shape=image;imageAspect=0;image=data:image/svg+xml,{encoded};'
            else:
                x,y,w,h=[r[z] for z in ('x','y','w','h')]
                attrs['style']=f'shape={"ellipse" if k=="ellipse" else "rectangle"};rounded={int(r.get("radius",0)>0)};absoluteArcSize=1;arcSize={r.get("radius",0)*4};fillColor={r["fill"]};strokeColor={r["stroke"]};strokeWidth={r["sw"]*2};'
            cell=ET.SubElement(root,'mxCell',attrs)
            ET.SubElement(cell,'mxGeometry',x=str((x-gx)*2),y=str((y-gy)*2),width=str(w*2),height=str(h*2),attrib={'as':'geometry'})
        ET.indent(mxfile)
        ET.ElementTree(mxfile).write(ROOT/f'{self.name}.drawio',encoding='utf-8',xml_declaration=True)
