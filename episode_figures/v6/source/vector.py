"""Native vector figure primitives at 2x final ICLR point coordinates.

SVG and PDF are publication masters. draw.io copies contain individually editable
text, shapes, connectors, and embedded camera images, with external font faces.
"""
from pathlib import Path
import base64
from html import escape
import json
import subprocess
import sys
from xml.etree import ElementTree as ET
from PIL import Image, ImageFont

ROOT=Path(__file__).resolve().parent
import canvas as legacy

OUT=ROOT/'rendered'
OUT.mkdir(exist_ok=True)
legacy.ROOT=OUT
legacy.ASSETS=ROOT.parent/'frames'
INK='#263A43'
MUTED='#66767C'
LINE='#CBD6D8'
BLUE='#506D9C'
TEAL='#347363'
AMBER='#866332'
RED='#A24E41'
PALE_BLUE='#EDF2FA'
PALE_TEAL='#EDF5F1'
PALE_WARM='#FAF4E8'
FONT_ROOT=ROOT.parents[2]/'figure1'/'style_reference'/'fonts'
FONT_URL='https://hellomuffin.github.io/cooksim-results-v6/figure1/style_reference/fonts/'
FACES=[('IBM Plex Sans','face-1.ttf','normal'),('IBM Plex Sans SemiBold','face-3.ttf','normal'),('IBM Plex Serif','face-4.ttf','italic'),('IBM Plex Mono','face-0.ttf','normal')]
_fonts={}


def width(text,size=16,family='IBM Plex Sans',italic=False):
    key=(family,italic)
    if key not in _fonts:
        path=subprocess.check_output(['fc-match','-f','%{file}',family+(':style=Italic' if italic else '')],text=True)
        _fonts[key]=ImageFont.truetype(path,1000)
    return _fonts[key].getlength(text)*size/1000


def wrap(text,maxwidth,size=16,family='IBM Plex Sans',italic=False):
    lines=[]
    for paragraph in text.split('\n'):
        current=''
        for word in paragraph.split():
            nxt=(current+' '+word).strip()
            if current and width(nxt,size,family,italic)>maxwidth:
                lines.append(current);current=word
            else:current=nxt
        lines.append(current)
    # Avoid single-word orphans when moving a word still respects the measure.
    if len(lines)>1 and len(lines[-1].split())==1 and len(lines[-2].split())>2:
        prev=lines[-2].split()
        last=prev[-1]+' '+lines[-1]
        if width(last,size,family,italic)<=maxwidth:
            lines[-2]=' '.join(prev[:-1]);lines[-1]=last
    return lines


class Figure(legacy.Canvas):
    def __init__(self,name,height,title):
        super().__init__(name,height,title)
        self.w=792
        self.output_width=396
        self.bounds=[]

    def text(self,x,y,text,size=16,weight=400,anchor='start',color=INK,family=None,italic=False,leading=1.25):
        family=family or ('IBM Plex Sans SemiBold' if weight>=600 else 'IBM Plex Sans')
        for i,line in enumerate(text.split('\n')):
            yy=y+i*size*leading
            super().text(x,yy,line,size,400,anchor,color,family,italic)
            tw=width(line,size,family,italic)
            left=x-({'start':0,'middle':tw/2,'end':tw}[anchor])
            self.bounds.append(dict(text=line,left=left,right=left+tw,top=yy-size,bottom=yy+size*.25,print_size=size/2,group='/'.join(self.stack)))

    def paragraph(self,x,y,w,text,size=16,weight=400,color=INK,family=None,italic=False,leading=1.25):
        family=family or ('IBM Plex Sans SemiBold' if weight>=600 else 'IBM Plex Sans')
        lines=wrap(text,w,size,family,italic)
        self.text(x,y,'\n'.join(lines),size,weight,color=color,family=family,italic=italic,leading=leading)
        return len(lines)*size*leading

    def photo(self,x,y,w,h,source,crop=None,border=LINE,rounded=False):
        if crop is None:
            iw,ih=Image.open(legacy.ASSETS/source).size
            crop=(0,0,iw,ih)
        self.image(x,y,w,h,source,crop)
        if rounded:
            radius=4 if rounded is True else float(rounded)
            # Identical native SVG clipping in the publication master and in
            # the embedded image element used by diagrams.net.
            self.parts[-1]=self.parts[-1].replace(f'width="{w}" height="{h}"/></clipPath>',f'width="{w}" height="{h}" rx="{radius}"/></clipPath>',1)
            rec=self.records[-1]
            rec['svg']=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><clipPath id="rounded-photo"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath></defs><g clip-path="url(#rounded-photo)">{rec["svg"]}</g></svg>'
        # The viewport crops only; evidence pixels are never retouched.
        if border:self.rect(x,y,w,h,'none',border,(4 if rounded is True else rounded) or 0,.7)

    def photo_fit(self,x,y,w,h,source,crop,border=LINE,rounded=False):
        """Contain the specified evidence crop; never clip a floor-plan edge."""
        factor=min(w/crop[2],h/crop[3])
        iw,ih=crop[2]*factor,crop[3]*factor
        self.photo(x+(w-iw)/2,y+(h-ih)/2,iw,ih,source,crop,border,rounded)

    def tag(self,x,y,w,text,color=TEAL,fill=PALE_TEAL,size=16,pad=8,leading=1.3):
        lines=wrap(text,w-pad*2,size)
        h=len(lines)*size*leading+pad*1.25
        self.rect(x,y,w,h,fill,'none',4)
        self.text(x+w/2,y+pad*.55+size,'\n'.join(lines),size,anchor='middle',color=color,leading=leading)
        return h

    def bubble(self,x,y,w,text,role='assistant',size=17,pad=11):
        color,fill=(BLUE,PALE_BLUE) if role=='assistant' else (TEAL,PALE_TEAL)
        lines=wrap(text,w-pad*2,size)
        h=len(lines)*size*1.3+pad*1.45
        self.rect(x,y,w,h,fill,'none',6)
        self.text(x+pad,y+pad*.7+size,'\n'.join(lines),size,color=INK,leading=1.3)
        # Small role rail keeps the roles identifiable without repeated headings.
        self.rect(x,y+9,2,h-18,color,'none',1)
        return h

    def action(self,x,y,w,text,size=15,color=TEAL):
        """Outlined action chip, deliberately distinct from filled speech bubbles."""
        lines=wrap(text,w-25,size)
        h=len(lines)*size*1.3+9
        self.rect(x,y,w,h,'#FFFFFF',color,3,.9)
        cy=y+h/2
        self.path([(x+7,cy-4),(x+11,cy),(x+7,cy+4)],color,1.1)
        self.text(x+18,y+size+3,'\n'.join(lines),size,color=color,leading=1.3)
        return h

    def rule(self,y,color=LINE):
        self.path([(8,y),(784,y)],color,.8)

    def drawio(self):
        """Preserve nested component groups for practical author co-editing."""
        super().drawio()
        path=OUT/f'{self.name}.drawio'
        tree=ET.parse(path);root=tree.find('.//root')
        byid={c.get('id'):c for c in root.findall('mxCell')}
        topnames=list(dict.fromkeys(r['group'].split('/')[0] for r in self.records if r['group']))
        topids={g:f'component-{i}' for i,g in enumerate(topnames)}
        origins={g:(float(byid[i].find('mxGeometry').get('x')),float(byid[i].find('mxGeometry').get('y'))) for g,i in topids.items()}
        nested={}
        for i,r in enumerate(self.records,2):
            parts=r['group'].split('/')
            if len(parts)<2:continue
            cell=byid[str(i)];geo=cell.find('mxGeometry');ox,oy=origins[parts[0]]
            if r['kind']=='edge':
                points=[(float(p.get('x'))+ox,float(p.get('y'))+oy) for p in geo.iter('mxPoint')]
                xs,ys=zip(*points);bounds=[min(xs),min(ys),max(xs),max(ys)]
            else:
                x,y=float(geo.get('x'))+ox,float(geo.get('y'))+oy
                bounds=[x,y,x+float(geo.get('width')),y+float(geo.get('height'))]
            for depth in range(2,len(parts)+1):
                name='/'.join(parts[:depth])
                if name not in nested:nested[name]=bounds[:]
                else:
                    b=nested[name];nested[name]=[min(b[0],bounds[0]),min(b[1],bounds[1]),max(b[2],bounds[2]),max(b[3],bounds[3])]
        ids={name:f'nested-component-{i}' for i,name in enumerate(nested)}
        for name in sorted(nested,key=lambda n:n.count('/')):
            x,y,x2,y2=nested[name];parent=name.rsplit('/',1)[0]
            px,py=nested[parent][:2] if parent in nested else origins[parent]
            cell=ET.SubElement(root,'mxCell',id=ids[name],parent=ids.get(parent,topids.get(parent)),vertex='1',style='group;',connectable='0')
            ET.SubElement(cell,'mxGeometry',x=str(x-px),y=str(y-py),width=str(x2-x),height=str(y2-y),attrib={'as':'geometry'})
        for i,r in enumerate(self.records,2):
            if r['group'] not in nested:continue
            cell=byid[str(i)];geo=cell.find('mxGeometry');ox,oy=origins[r['group'].split('/')[0]]
            nx,ny=nested[r['group']][:2]
            cell.set('parent',ids[r['group']])
            if r['kind']=='edge':
                for point in geo.iter('mxPoint'):
                    point.set('x',str(float(point.get('x'))+ox-nx));point.set('y',str(float(point.get('y'))+oy-ny))
            else:
                geo.set('x',str(float(geo.get('x'))+ox-nx));geo.set('y',str(float(geo.get('y'))+oy-ny))
        ET.indent(tree);tree.write(path,encoding='utf-8',xml_declaration=True)

    def save(self):
        css=[]
        for family,file,style in FACES:
            data=base64.b64encode((FONT_ROOT/file).read_bytes()).decode()
            css.append(f'@font-face{{font-family:"{family}";font-style:{style};font-weight:400;src:url(data:font/ttf;base64,{data}) format("truetype");}}')
        colors=set(r['color'] for r in self.records if r['kind']=='edge')
        markers=''.join(f'<marker id="arrow-{c[1:]}" viewBox="0 0 6 6" refX="5.5" refY="3" markerWidth="7" markerHeight="7" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L6,3 L0,6 Z" fill="{c}"/></marker>' for c in colors)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="396pt" height="{self.h/2}pt" viewBox="0 0 792 {self.h}"><title>{escape(self.title)}</title><desc>Engine-rendered observations with editable vector annotations. Authored dialogue is illustrative.</desc><defs><style>{"".join(css)}</style>{markers}</defs><rect width="792" height="{self.h}" fill="white"/>'+''.join(self.parts)+'</svg>'
        target=OUT/f'{self.name}.svg'
        target.write_text(svg)
        (OUT/f'{self.name}.elements.json').write_text(json.dumps(self.records,indent=2))
        (OUT/f'{self.name}.text_audit.json').write_text(json.dumps(self.bounds,indent=2))
        for fmt in ['pdf','png']:
            cmd=['inkscape',str(target),f'--export-type={fmt}',f'--export-filename={target.with_suffix("."+fmt)}']
            if fmt=='png':cmd.append('--export-dpi=240')
            subprocess.run(cmd,check=True,capture_output=True)
        self.drawio()
        path=OUT/f'{self.name}.drawio'
        tree=ET.parse(path)
        tree.find('.//mxGraphModel').set('extFonts','|'.join((family+' Italic' if style=='italic' else family)+'^'+FONT_URL+file for family,file,style in FACES))
        for cell in tree.findall('.//mxCell'):
            s=cell.get('style','')
            if 'fontFamily=IBM Plex Serif;' in s:
                cell.set('style',s.replace('fontFamily=IBM Plex Serif;','fontFamily=IBM Plex Serif Italic;').replace('fontStyle=2;','fontStyle=0;'))
        ET.indent(tree)
        tree.write(path,encoding='utf-8',xml_declaration=True)
        outside=[b for b in self.bounds if b['left']<-.1 or b['right']>792.1 or b['top']<-.1 or b['bottom']>self.h+.1]
        print(self.name, 'size', f'396 × {self.h/2} pt', 'min font', min(b['print_size'] for b in self.bounds), 'outside', outside)
