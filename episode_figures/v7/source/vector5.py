"""Wide native-vector canvases with open Manrope typography."""
from pathlib import Path
from html import escape
from xml.etree import ElementTree as ET
import base64,json,subprocess
from vector import Figure,OUT,width,wrap

ROOT=Path(__file__).resolve().parent
FONT_DIR=ROOT.parent/'fonts'
FACES=[('Manrope','Manrope-Regular.ttf'),('Manrope SemiBold','Manrope-SemiBold.ttf')]
INK='#293C49';MUTED='#586973';LINE='#B1BFC6'
BLUE='#405F7B';COPPER='#85573F';PALE_BLUE='#EFF3F7';PALE_COPPER='#F7F0E9'

class WideFigure(Figure):
    def __init__(self,name,height,title,canvas_width=1800):
        super().__init__(name,height,title);self.w=canvas_width
    def text(self,x,y,text,size=32,weight=400,anchor='start',color=INK,family=None,italic=False,leading=1.4):
        family=family or ('Manrope SemiBold' if weight>=600 else 'Manrope')
        first=len(self.bounds)
        super().text(x,y,text,size,weight,anchor,color,family,italic,leading)
        for b in self.bounds[first:]:b['print_size']=size*396/self.w
    def paragraph(self,x,y,w,text,size=32,weight=400,color=INK,family=None,italic=False,leading=1.4):
        family=family or ('Manrope SemiBold' if weight>=600 else 'Manrope')
        lines=wrap(text,w,size,family,italic)
        self.text(x,y,'\n'.join(lines),size,weight,color=color,family=family,italic=italic,leading=leading)
        return len(lines)*size*leading
    def bubble(self,x,y,w,text,role='assistant',size=32,pad=14):
        color,fill=(BLUE,PALE_BLUE) if role=='assistant' else (COPPER,PALE_COPPER)
        lines=wrap(text,w-pad*2,size,'Manrope')
        h=len(lines)*size*1.3+pad*1.5
        self.rect(x,y,w,h,fill,color,10,1.5)
        self.text(x+pad,y+pad*.65+size,'\n'.join(lines),size,color=INK,leading=1.3)
        return h
    def save(self):
        css=[]
        for family,file in FACES:
            data=base64.b64encode((FONT_DIR/file).read_bytes()).decode()
            css.append(f'@font-face{{font-family:"{family}";font-weight:400;src:url(data:font/ttf;base64,{data}) format("truetype");}}')
        colors=set(r['color'] for r in self.records if r['kind']=='edge')
        markers=''.join(f'<marker id="arrow-{c[1:]}" viewBox="0 0 6 6" refX="5.5" refY="3" markerWidth="11" markerHeight="11" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L6,3 L0,6 Z" fill="{c}"/></marker>' for c in colors)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="396pt" height="{self.h*396/self.w}pt" viewBox="0 0 {self.w} {self.h}"><title>{escape(self.title)}</title><desc>Authored dialogue with unretouched engine observations. Timeline positions are schematic, not measured latency.</desc><defs><style>{"".join(css)}</style>{markers}</defs><rect width="{self.w}" height="{self.h}" fill="white"/>'+''.join(self.parts)+'</svg>'
        target=OUT/f'{self.name}.svg';target.write_text(svg)
        (OUT/f'{self.name}.elements.json').write_text(json.dumps(self.records,indent=2))
        (OUT/f'{self.name}.text_audit.json').write_text(json.dumps(self.bounds,indent=2))
        for fmt in ('pdf','png'):
            cmd=['inkscape',str(target),f'--export-type={fmt}',f'--export-filename={target.with_suffix("."+fmt)}']
            if fmt=='png':cmd.append('--export-dpi=240')
            subprocess.run(cmd,check=True,capture_output=True)
        self.drawio()
        p=OUT/f'{self.name}.drawio';tree=ET.parse(p)
        tree.find('.//mxGraphModel').set('extFonts','|'.join(f'{family}^https://hellomuffin.github.io/cooksim-results-v6/episode_figures/v5/fonts/{file}' for family,file in FACES))
        ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
        outside=[b for b in self.bounds if b['left']<-.1 or b['right']>self.w+.1 or b['top']<-.1 or b['bottom']>self.h+.1]
        print(self.name,396,self.h*396/self.w,'outside',outside,flush=True)
