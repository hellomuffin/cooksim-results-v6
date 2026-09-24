"""Shared LaTeX rendering helpers; no experiment-data loading at import time."""
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent

STYLE = r'''% Shared packages/macros for the three input-ready table files.
\usepackage[T1]{fontenc}
\usepackage{times,booktabs,array,amsmath,graphicx}
\usepackage{xcolor,colortbl}
\definecolor{ivgink}{HTML}{172F39}
\definecolor{ivgcook}{HTML}{FAF6F0}
\definecolor{ivgvh}{HTML}{EDF8F5}
\definecolor{ivgscreen}{HTML}{F4EFF8}
\definecolor{ivgquality}{HTML}{EFF5F9}
\definecolor{ivgmuted}{HTML}{5F6C76}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{K}[2]{>{\columncolor{#1}\centering\arraybackslash}p{#2}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcommand{\ivghead}[1]{{\sffamily\fontsize{7.3}{8.5}\selectfont\bfseries #1}}
\newcommand{\ivgvhead}[1]{{\sffamily\fontsize{7.2}{8.5}\selectfont\rotatebox{90}{\strut #1}}}
\newcommand{\ivgband}[2]{\midrule\rowcolor{white}\multicolumn{#1}{@{}l@{}}{\strut{\sffamily\fontsize{7.6}{9}\selectfont\bfseries #2}}\\[1pt]}
\newcommand{\ivgmissing}{\textcolor{ivgmuted}{---}}
\newcommand{\ivgsd}[2]{#1\,{\fontsize{6.5}{7}\selectfont\textcolor{ivgmuted}{$\pm$#2}}}
\newcommand{\ivgnote}[1]{\par\vspace{5pt}{\fontsize{8}{9.5}\selectfont\noindent #1\par}}
'''

def begin(spec, font='8.1', leading='10.2'):
    return [r'\begingroup', r'\setlength{\tabcolsep}{0pt}',
            r'\renewcommand{\arraystretch}{1.02}',
            rf'\fontsize{{{font}}}{{{leading}}}\selectfont',
            r'\begin{tabular}{@{}' + spec + r'@{}}', r'\toprule']


def finish(lines, note):
    return '\n'.join(lines + [r'\bottomrule', r'\end{tabular}\par', r'\endgroup',
                             r'\ivgnote{' + note + '}']) + '\n'

def wrapper(name, title, caption, number):
    return rf'''% Standalone preview: same 5.5-inch text width and Times font as the ICLR paper.
\documentclass[10pt]{{article}}
\usepackage[paperwidth=6.3in,paperheight=10in,left=.4in,right=.4in,top=.35in,bottom=.35in]{{geometry}}
\input{{table_style.tex}}
\pagestyle{{empty}}
\setlength{{\parindent}}{{0pt}}
\begin{{document}}
\newcommand{{\ivgnotes}}{{}}
\renewcommand{{\ivgnote}}[1]{{\gdef\ivgnotes{{#1}}}}
\input{{{name}.tex}}
\par\vspace{{6pt}}
{{\fontsize{{8.8}}{{10.3}}\selectfont\textsf{{\textbf{{Table {number} {title}}}}} {caption} \ivgnotes\par}}
\end{{document}}
'''


def render(name, tectonic):
    result = subprocess.run([tectonic, '--keep-logs', f'{name}_preview.tex'], cwd=HERE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout)
    import fitz
    doc = fitz.open(HERE / f'{name}_preview.pdf')
    assert len(doc) == 1, f'{name} spills to {len(doc)} pages'
    page = doc[0]
    blocks = page.get_text('blocks')
    box = fitz.Rect(blocks[0][:4])
    for block in blocks[1:]:
        box |= fitz.Rect(block[:4])
    # Preserve the exact paper text width; trim only page margins / unused height.
    crop = fitz.Rect(24.8, 20, page.rect.width-24.8, box.y1+7)
    page.set_cropbox(crop)
    doc.save(HERE / f'{name}.pdf')
    page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False).save(HERE / f'{name}.png')
    (HERE / f'{name}.svg').write_text(page.get_svg_image(text_as_path=True))
    print(f'{name}: {crop.width:.1f} x {crop.height:.1f} pt; 1 page')
    log = (HERE / f'{name}_preview.log').read_text()
    for line in log.splitlines():
        if 'Overfull' in line:
            print(f'LAYOUT WARNING {name}: {line}')
