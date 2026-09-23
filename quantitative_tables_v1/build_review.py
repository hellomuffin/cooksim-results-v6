#!/usr/bin/env python3
"""Build paper-width LaTeX table drafts from the experiment Markdown snapshots.

No episode reruns or regrading. Sources are rounded, provisional exports.
Run from this directory with Python + PyMuPDF and Tectonic installed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EXPERIMENT = ROOT / 'experiment'
GROUPS = [
    ('Frontier API models', [
        ('GPT-6 Astra', 'GPT-6 Astra'),
        ('Gemini 3.1 Pro', 'Gemini 3.1 Pro'),
        ('Gemini 3.8 Flash', 'Gemini 3.8 Flash')]),
    ('Real-time streaming API models', [
        ('Gemini 3.8 Live', 'Gemini 3.8 Live (polled)'),
        ('GPT-realtime 2.1', 'GPT-Realtime 2.1 (polled)'),
        ('Gemini 3.8 Live (native)', 'Gemini 3.8 Live (native)'),
        ('GPT-realtime 2.1 (native)', 'GPT-Realtime 2.1 (native)')]),
    ('Open-weight non-streaming VLMs', [
        ('Qwen3.8-27B', 'Qwen3.8-27B'),
        ('Molmo2-8B', 'Molmo2-8B'),
        ('InternVideo3-8B', 'InternVideo3-8B'),
        ('GLM-4.6V Flash', 'GLM-4.6V-Flash'),
        ('Kimi-VL Thinking', 'Kimi-VL-A3B-Thinking'),
        ('Muse Glimmer', 'Muse Glimmer')]),
    ('Open-weight streaming VLMs', [
        ('MiniCPM-o', 'MiniCPM-o 4.5'),
        ('Qwen3-Omni 30B', 'Qwen3-Omni-30B'),
        ('Proact-VL', 'Proact-VL'),
        ('StreamingVLM', 'StreamingVLM')]),
]
MODELS = [m for _, models in GROUPS for m in models]
ENGINES = [('cooksim', 'CookSim'), ('vhhome', 'VHSim'), ('screensim', 'ScreenSim')]
DIMS = ['Factual grounding', 'Situational relevance', 'Actionable guidance',
        'User intent uptake', 'Guidance conciseness']
PROVENANCE = []


def read_tables(relative):
    path = EXPERIMENT / relative
    source = path.read_text()
    PROVENANCE.append({'source': str(path.relative_to(ROOT)),
                       'sha256': hashlib.sha256(source.encode()).hexdigest()})
    out = []
    active = None
    for line in source.splitlines():
        if line.startswith('| Seat |'):
            active = [[], []]
            active[0] = [x.strip() for x in line.strip('|').split('|')]
            out.append(active)
        elif line.startswith('|') and active is not None:
            cells = [x.strip() for x in line.strip('|').split('|')]
            if all(re.fullmatch(r'[-: ]+', c) for c in cells):
                continue
            assert len(cells) == len(active[0]), (relative, cells)
            active[1].append(cells)
        elif active is not None:
            active = None
    return out


def value(x):
    return None if x in ('–', '—', '-', '') else float(x)


def mean_runs(s):
    vals = [float(v.strip()) for v in s.split('/')]
    return sum(vals) / len(vals)


def mean_sd(s):
    a, b = s.split('±')
    return float(a), float(b)


task, rubric = {}, {}
for key, _ in ENGINES:
    tab = read_tables(f'01_task_outcome_efficiency_detection/{key}.md')[1]
    task[key] = {}
    for row in tab[1]:
        task[key][row[0]] = {
            'n_runs': row[1], 'success': mean_sd(row[3]),
            'anytime': mean_sd(row[5]), 'timing': mean_sd(row[7]),
            'f1': mean_sd(row[9]), 'action': mean_runs(row[10]),
            'conversation': mean_runs(row[11])}
    tab = read_tables(f'02_interaction_quality_rubric/{key}.md')[0]
    rubric[key] = {}
    for cells in tab[1]:
        row = dict(zip(tab[0], cells))
        rubric[key][row['Seat']] = {
            'n': int(row['n episodes']),
            'overall': value(row.get('AQ (full 16)', row.get('AQ'))),
            **{dim: value(row[dim]) for dim in DIMS}}
qa_table = read_tables('03_qa_proactive/cooksim.md')[0]
qa = {r[0]: dict(zip(qa_table[0][1:], r[1:])) for r in qa_table[1]}
# CookSim is the common ordering anchor: native configurations exist only there.
GROUPS = [(name, sorted(models, key=lambda m: -task['cooksim'][m[0]]['success'][0]))
          for name, models in GROUPS]
MODELS = [m for _, models in GROUPS for m in models]

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


def score(v, rank=None):
    if v is None:
        return r'\ivgmissing'
    s = str(round(v * 100))
    if rank == 1:
        return r'\textbf{' + s + '}'
    if rank == 2:
        return r'\underline{' + s + '}'
    return s


def ranking(values):
    levels = sorted({round(v*100) for v in values if v is not None}, reverse=True)
    return {v: i+1 for i, v in enumerate(levels[:2])}


def cell(v, ranks=None):
    rank = ranks.get(round(v*100)) if ranks and v is not None else None
    return score(v, rank)


def begin(spec, font='8.1', leading='10.2'):
    return [r'\begingroup', r'\setlength{\tabcolsep}{0pt}',
            r'\renewcommand{\arraystretch}{1.02}',
            rf'\fontsize{{{font}}}{{{leading}}}\selectfont',
            r'\begin{tabular}{@{}' + spec + r'@{}}', r'\toprule']


def finish(lines, note):
    return '\n'.join(lines + [r'\bottomrule', r'\end{tabular}\par', r'\endgroup',
                             r'\ivgnote{' + note + '}']) + '\n'


def task_table():
    # Sum of column widths = linewidth. No resizebox or scaled typography.
    colors = ['ivgcook', 'ivgvh', 'ivgscreen']
    spec = r'L{.25\linewidth}' + ''.join(''.join(r'K{' + col + '}{' + width + r'\linewidth}'
                for width in ['.085', '.055', '.055', '.055']) for col in colors)
    lines = begin(spec)
    lines += [r'& \multicolumn{4}{c}{\ivghead{CookSim}} & \multicolumn{4}{c}{\ivghead{VHSim}} & \multicolumn{4}{c}{\ivghead{ScreenSim}} \\',
              r'\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}',
              r'\ivghead{Assistant} & ' + ' & '.join([r'\ivgvhead{In-time success}', r'\ivgvhead{Action efficiency}', r'\ivgvhead{Conversation efficiency}', r'\ivgvhead{Detection F1}']*3) + r'\\']
    maxima = {e: {m: ranking(task[e][k][m][0] if m in ('success', 'f1') else task[e][k][m]
                            for k, _ in MODELS if k in task[e])
                   for m in ('success', 'f1', 'action', 'conversation')} for e, _ in ENGINES}
    def row(key, label, highlight=True):
        cells = [label]
        for engine, _ in ENGINES:
            d = task[engine].get(key)
            if d is None:
                cells.extend([r'\ivgmissing']*4)
                continue
            s, sd = d['success']
            mark = cell(s, maxima[engine]['success'] if highlight else None)
            cells.extend([r'\ivgsd{' + mark + '}{' + str(round(sd*100)) + '}',
                          cell(d['action'], maxima[engine]['action'] if highlight else None),
                          cell(d['conversation'], maxima[engine]['conversation'] if highlight else None),
                          cell(d['f1'][0], maxima[engine]['f1'] if highlight else None)])
        return ' & '.join(cells) + r'\\'
    for group, models in GROUPS:
        lines.append(r'\ivgband{13}{' + group + '}')
        lines.extend(row(*m) for m in models)
    lines.append(r'\ivgband{13}{Reference conditions}')
    # Reference names differ across export files; normalize without changing data.
    task['screensim']['Silent control'] = task['screensim']['Silent floor (reference)']
    lines.append(row('Silent control', 'No assistance', False))
    lines.append(row('Oracle ceiling (reference)', 'Scripted reference', False))
    return finish(lines, r'Scores are on a 0--100 scale; success includes run SD. Within each family, models are ordered by CookSim success. Bold and underline mark the highest and second-highest assistant values in each metric column, with ties at displayed precision. Reference conditions are not ranked; dashes indicate unavailable results.')


def rubric_table(engine=None):
    if engine:
        spec = r'L{.28\linewidth}K{ivgscreen}{.10\linewidth}' + r'K{ivgquality}{.124\linewidth}'*5
        lines = begin(spec, '8.6', '10.7')
        labels = [r'\ivghead{Assistant}', r'\ivghead{Overall}']
    else:
        spec = (r'L{.25\linewidth}K{ivgcook}{.09\linewidth}K{ivgvh}{.09\linewidth}K{ivgscreen}{.09\linewidth}'
                + r'K{ivgquality}{.096\linewidth}'*5)
        lines = begin(spec, '8.1', '10.2')
        lines.extend([r'& \multicolumn{3}{c}{\ivghead{Overall quality}} & \multicolumn{5}{c}{\ivghead{Rubric dimensions: three-environment mean}} \\',
                      r'\cmidrule(lr){2-4}\cmidrule(lr){5-9}'])
        labels = [r'\ivghead{Assistant}'] + [r'\ivgvhead{' + name + '}' for _, name in ENGINES]
    labels += [r'\ivgvhead{' + name + '}' for name in DIMS]
    lines += [' & '.join(labels) + r'\\']
    rows = {}
    for key, _ in MODELS:
        if engine:
            d = rubric[engine].get(key)
            rows[key] = ([d['overall']] + [d[x] for x in DIMS]) if d else [None]*6
        else:
            ds = [rubric[e].get(key) for e, _ in ENGINES]
            vals = [d['overall'] if d else None for d in ds]
            vals.extend([sum(d[x] for d in ds)/3 for x in DIMS] if all(ds) else [None]*5)
            rows[key] = vals
    maxima = [ranking(x[i] for x in rows.values()) for i in range(len(next(iter(rows.values()))))]
    for group, models in GROUPS:
        present = [(k, label) for k, label in models if not engine or k in rubric[engine]]
        if not present:
            continue
        lines.append(r'\ivgband{' + ('7' if engine else '9') + '}{' + group + '}')
        for key, label in present:
            lines.append(' & '.join([label] + [cell(v, maxima[i]) for i, v in enumerate(rows[key])]) + r'\\')
    note = (r'Scores are on a 0--100 scale (run 1). Overall: full 16-item CookSim rubric with mandatory-failure gating, not the mean of the five displayed dimensions. '
            + (r'Dimension scores are averaged within episodes and then across episodes.' if engine else
               r'Dimensions: equal-weight means across all three environments; unavailable for CookSim-only native configurations.')
            + r' Bold / underline: highest / second-highest per column. Row order follows CookSim success within each family.')
    return finish(lines, note.replace(r'CookSim\textquotesingle s', "CookSim's"))


def qa_table_tex():
    fields = ['Q1 order', 'Q2 count', 'Q3 timing', 'Q4 did-it', 'Q10 proactive']
    spec = r'L{.27\linewidth}C{.08\linewidth}' + r'K{ivgcook}{.13\linewidth}'*4 + r'K{ivgvh}{.13\linewidth}'
    lines = begin(spec, '8.6', '10.7')
    lines.extend([r'& & \multicolumn{4}{c}{\ivghead{Question answering}} & \ivghead{Requests} \\',
                  r'\cmidrule(lr){3-6}\cmidrule(lr){7-7}',
                  r'\ivghead{Assistant} & \ivghead{Items} & \ivghead{Temporal\newline order} & \ivghead{Action\newline counting} & \ivghead{Cooking\newline time} & \ivghead{Event\newline recall} & \ivghead{Timely\newline alerts} \\'])
    maxima = {f: ranking(value(qa[k][f]) for k, _ in MODELS) for f in fields}
    for group, models in GROUPS:
        lines.append(r'\ivgband{7}{' + group + '}')
        for key, label in models:
            d = qa[key]
            cells = [label, d['n items']] + [cell(value(d[f]), maxima[f]) for f in fields]
            lines.append(' & '.join(cells) + r'\\')
    return finish(lines, r'CookSim, run 1; scores on a 0--100 scale. Items: scored questions and requests; dashes: no scored items. Bold / underline: highest / second-highest per category. Rows follow CookSim success within each family. Alerts receive credit only within the valid response window.')


CAPTIONS = {
    'task_performance': ('Task performance.', 'Task success, execution efficiency, and error detection across three environments. Results summarize three independent runs.'),
    'interaction_quality': ('Interaction quality.', 'Overall quality in each environment and five complementary dimensions of assistance, evaluated with the full CookSim rubric.'),
    'qa_proactive': ('Question answering and proactive assistance.', 'Tracking task history and fulfilling standing requests during cooking episodes.'),
}


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tectonic', default='/tmp/ivg-paper-figures.gX58U6/tectonic')
    args = parser.parse_args()
    (HERE / 'table_style.tex').write_text(STYLE)
    content = {'task_performance': task_table(), 'interaction_quality': rubric_table(),
               'qa_proactive': qa_table_tex()}
    for i, (name, text) in enumerate(content.items(), 1):
        (HERE / f'{name}.tex').write_text(text)
        title, caption = CAPTIONS[name]
        (HERE / f'{name}_preview.tex').write_text(wrapper(name, title, caption, i))
        render(name, args.tectonic)
    for key, label in ENGINES:
        name = 'rubric_' + key
        (HERE / f'{name}.tex').write_text(rubric_table(key))
        (HERE / f'{name}_preview.tex').write_text(wrapper(name, f'Interaction quality in {label}.',
                                                       'Unaggregated scores for layout review.', 'S'))
        render(name, args.tectonic)
    (HERE / 'source_data.json').write_text(json.dumps({
        'source_files': PROVENANCE, 'task': task, 'rubric': rubric, 'qa': qa,
        'notes': ['Draft values from rounded Markdown exports; no new grading.',
                  'Rubric overall = full 16 items, including VHSim AQ (full 16).',
                  'Rubric dimensions = equal-weight average of three environment means.',
                  'Task success +/- SD copied from exports; efficiency = average of three reported run means.',
                  'No significance tests computed; bold/underline denote numerical first/second at displayed precision.',
                  'Within each family, every table uses descending three-run CookSim success as the shared row order.',
                  'Model roster follows the latest user list; native and polled configurations remain separate.']}, indent=2))
    with zipfile.ZipFile(HERE / 'latex_sources.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(HERE.glob('*.tex')):
            z.write(path, path.name)
        z.write(HERE / 'source_data.json', 'source_data.json')
        z.write(__file__, 'build_review.py')


if __name__ == '__main__':
    main()
