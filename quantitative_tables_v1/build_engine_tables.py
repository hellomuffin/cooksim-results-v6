#!/usr/bin/env python3
"""Engine-specific paper tables from precise, precomputed episode aggregates."""
from pathlib import Path
import json
import zipfile
import build_review as shared

HERE = Path(__file__).resolve().parent
ENGINES = [('cooksim', 'CookSim'), ('vhhome', 'VHSim'), ('screensim', 'ScreenSim')]
GROUPS = [
    ('Frontier API models', [('gpt-6-astra','GPT-6 Astra'),
      ('gemini-3.1-pro-preview','Gemini 3.1 Pro'),('gemini-3.8-flash','Gemini 3.8 Flash')]),
    ('Real-time streaming API models', [('gemini-3.8-live','Gemini 3.8 Live'),
      ('gpt-realtime-2.1','GPT-Realtime 2.1')]),
    ('Open-weight non-streaming VLMs', [('qwen3.8-27b','Qwen3.8-27B'),
      ('molmo2-8b','Molmo2-8B'),('internvideo3-8b','InternVideo3-8B'),
      ('glm-4.6v-flash','GLM-4.6V-Flash'),('kimi-vl-thinking','Kimi-VL-A3B-Thinking'),
      ('museglimmer','Muse Glimmer')]),
    ('Open-weight streaming VLMs', [('minicpmo','MiniCPM-o 4.5'),
      ('qwen3-omni-30b-a3b','Qwen3-Omni-30B'),('proact-vl','Proact-VL'),
      ('streamingvlm','StreamingVLM')])]
METRICS = ['success','action','conversation','efficiency','truthful','sensible',
           'helpful','listens','economy','overall']


def tag_for(engine, tag):
    return tag+'__native' if engine=='cooksim' and tag in ('gemini-3.8-live','gpt-realtime-2.1') else tag


def value(record, metric):
    return record.get(metric) if metric in METRICS[:4] else record['quality'].get(metric)


def displayed(v):
    return float(f'{100*v:.1f}')


def table(engine, data):
    # 397.486 pt total at 5.5 in. Horizontal, two-line subheaders.
    widths = [82,29,24,41,24,33,35,34,33,38,24]
    colors = ['ivgsuccess']+['ivgeff']*3+['ivgrubric']*6
    spec = f'L{{{.999*widths[0]/sum(widths):.6f}\\linewidth}}'+''.join(f'K{{{c}}}{{{.999*w/sum(widths):.6f}\\linewidth}}' for c,w in zip(colors,widths[1:]))
    lines = shared.begin(spec, '8', '10.5')
    lines += [r'& \multicolumn{1}{c}{\ivghead{Success}} & \multicolumn{3}{c}{\ivghead{Efficiency}} & \multicolumn{6}{c}{\ivghead{Interaction quality}} \\',
              r'\cmidrule(lr){2-2}\cmidrule(lr){3-5}\cmidrule(lr){6-11}']
    heads = ['Assistant','In-time','Action','Conversation','Overall',
             r'Factual\\grounding',r'Situational\\relevance',r'Actionable\\guidance',
             r'User intent\\uptake',r'Guidance\\conciseness','Overall']
    lines.append(' & '.join(r'\ivgsub{'+h+'}' for h in heads)+r'\\[2pt]')
    selected = [data[tag_for(engine,t)] for _,members in GROUPS for t,_ in members]
    ranks = {m:sorted({displayed(value(d,m)) for d in selected if value(d,m) is not None},reverse=True)[:2] for m in METRICS}
    def row(tag,label,rank=True):
        record = data[tag]
        cells = [label]
        for m in METRICS:
            v = value(record,m)
            if v is None:
                cells.append(r'\ivgmissing')
                continue
            s=f'{100*v:.1f}'
            if rank and displayed(v) in ranks[m]:
                s = ('\\textbf{' if ranks[m].index(displayed(v))==0 else '\\underline{')+s+'}'
            cells.append(s)
        return ' & '.join(cells)+r'\\'
    for group,members in GROUPS:
        lines.append(r'\ivgband{11}{'+group+'}')
        members = sorted(members,key=lambda x:-data[tag_for(engine,x[0])]['success'])
        lines.extend(row(tag_for(engine,t),label) for t,label in members)
    references = [('silent','No assistance'),('silent floor','No assistance'),('oracle ceiling','Scripted reference')]
    references = [(t,l) for t,l in references if t in data]
    if references:
        lines.append(r'\ivgband{11}{Reference conditions}')
        lines.extend(row(t,l,False) for t,l in references)
    return shared.finish(lines, r'All scores are on a 0--100 scale ($\uparrow$). Success and efficiency are three-run means; efficiency is measured on in-time successes, with persona-weighted overall scores. Rubrics use run 1 and the full 16-item overall score. Bold/underline indicate the best/second-best assistant in each column; dashes denote unavailable scores.')


def webpage():
    sections = '\n'.join(f'''<section id="{key}"><div class="section-head"><div><span class="eyebrow">TABLE {i}</span><h2>{name}</h2></div><div class="downloads"><a href="engine_{key}.pdf">PDF ↗</a><a href="engine_{key}.tex">LaTeX ↓</a></div></div><div class="paper"><img src="engine_{key}.svg" alt="{name} results: success, efficiency and interaction quality, with four model families"></div></section>''' for i,(key,name) in enumerate(ENGINES,1))
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Interactive Visual Gym · Results tables</title>
<style>
:root{font-family:Inter,system-ui,sans-serif;color:#203740;background:#f5f6f6;font-synthesis:none}*{box-sizing:border-box}body{margin:0}header,main{max-width:1060px;margin:auto;padding:34px 28px}header{padding-bottom:22px}.eyebrow{font-size:11px;letter-spacing:.13em;font-weight:700;color:#627981}h1{font-size:30px;letter-spacing:-.035em;margin:12px 0}h2{font-size:21px;margin:5px 0}p{font-size:14px;line-height:1.65;max-width:830px;color:#52646d;margin:9px 0}nav{background:#ffffffed;border-block:1px solid #dfe6e7;position:sticky;top:0;z-index:2;backdrop-filter:blur(12px)}.nav-inner{max-width:1060px;padding:12px 28px;margin:auto;display:flex;gap:24px;align-items:center}a{color:#2b6876;text-decoration:none;font-size:13px;font-weight:600}a:hover{text-decoration:underline}.scale{margin-left:auto;display:flex;gap:5px}button{border:1px solid #d7e1e3;background:white;padding:7px 11px;border-radius:6px;color:#45606a;cursor:pointer}button.active{background:#243f4a;color:white;border-color:#243f4a}main{padding-top:22px}section{background:white;border:1px solid #dce4e6;border-radius:12px;padding:22px 26px;margin-bottom:26px;scroll-margin-top:78px}.section-head{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #e8edef;padding-bottom:13px;margin-bottom:20px}.downloads{display:flex;gap:20px}.paper{overflow:auto;text-align:center}.paper img{width:100%;max-width:920px;display:block;margin:auto}.paper-size .paper img{width:536px;max-width:none}.legend{display:flex;gap:17px;flex-wrap:wrap;font-size:12px;margin:17px 0;color:#536670}.legend span:before{content:'';display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:7px;vertical-align:-1px}.success:before{background:#f7e9eb}.eff:before{background:#e8f3ed}.rubric:before{background:#e9f0fa}details{background:#edf2f3;padding:16px 20px;border-radius:9px;margin-bottom:24px}summary{cursor:pointer;font-size:14px;font-weight:600}.formula{font-family:Georgia,serif;color:#243f4a;font-size:16px}.footer{display:flex;gap:20px;flex-wrap:wrap;padding:4px 0 24px}small{font-size:12px;color:#687e86}@media(max-width:650px){header,main{padding:23px 14px}.nav-inner{padding:10px 14px;gap:13px;flex-wrap:wrap}.scale{margin-left:0}section{padding:17px 10px}h1{font-size:26px}.paper img{min-width:650px}.paper-size .paper img{min-width:536px}.downloads{gap:12px}.legend{gap:12px}}
</style></head><body><header><span class="eyebrow">INTERACTIVE VISUAL GYM / TABLE REVIEW / V3</span><h1>Three environments. Three aspects.</h1><p>One table per engine, combining task success, persona-weighted efficiency, and interaction quality. Models are sorted by that engine’s success within each of the four families. Native streaming settings only.</p><div class="legend"><span class="success">Success</span><span class="eff">Efficiency</span><span class="rubric">Interaction quality</span></div><small>One decimal · best bold · second best underlined · actual LaTeX rendering at a 5.5-inch paper width</small></header>
<nav><div class="nav-inner"><a href="#cooksim">CookSim</a><a href="#vhhome">VHSim</a><a href="#screensim">ScreenSim</a><div class="scale"><button id="fit" class="active">Fit page</button><button id="paper">Paper width</button></div></div></nav><main>
<details><summary>How the overall efficiency and uncertainty are computed</summary><p>For each successfully completed episode, combine action and conversation efficiency using the persona’s speed preference and interruption preference, respectively. These are the existing 1–3 questionnaire levels, not fitted weights.</p><p class="formula">Overall = (w<sub>speed</sub> · Action + w<sub>interruption</sub> · Conversation) / (w<sub>speed</sub> + w<sub>interruption</sub>)</p><p>Average episode scores within each run, then average the run means. All three efficiency columns use in-time successes only; a run with no successes contributes no efficiency estimate. Success is the mean of three run-level rates. The previous ± values were population standard deviations across runs, not confidence intervals; they remain in the downloadable data, not the main tables.</p><p>Interaction quality reports the five agreed rubric dimensions and the full 16-item overall score from existing run-1 judgments. Overall is not an unweighted average of the five displayed columns. Numerical highlights do not indicate statistical significance.</p></details>
''' + sections + '''<div class="footer"><a href="engine_latex_sources.zip">Download all three tables + sources ↓</a><a href="engine_source_data.json">Precise scores + run SD ↓</a><a href="qa_proactive.pdf">Previous QA / proactive draft ↗</a></div><small>Draft for discussion. No model reruns or regrading. The Overleaf manuscript has not been changed.</small></main><script>for(const id of ['fit','paper'])document.getElementById(id).onclick=()=>{document.body.classList.toggle('paper-size',id==='paper');for(const x of ['fit','paper'])document.getElementById(x).classList.toggle('active',x===id)};</script></body></html>'''


def main():
    style = shared.STYLE + r'''
\definecolor{ivgsuccess}{HTML}{F8EDF0}
\definecolor{ivgeff}{HTML}{EDF6F0}
\definecolor{ivgrubric}{HTML}{EFF3FA}
\renewcommand{\ivghead}[1]{{\sffamily\fontsize{7.2}{8.5}\selectfont\bfseries #1}}
\newcommand{\ivgsub}[1]{{\sffamily\fontsize{6.6}{7.6}\selectfont\begin{tabular}[b]{@{}c@{}}#1\end{tabular}}}
'''
    (HERE/'engine_table_style.tex').write_text(style)
    source = {}
    for i,(key,label) in enumerate(ENGINES,1):
        d=json.loads((HERE/f'{key}_metrics.json').read_text())
        source[key]=d
        d['display_mapping']={label:tag_for(key,tag) for _,members in GROUPS for tag,label in members}
        name='engine_'+key
        (HERE/f'{name}.tex').write_text(table(key,d['models']))
        tex=shared.wrapper(name,f'Visual assistance in {label}.','',i).replace('table_style.tex','engine_table_style.tex')
        (HERE/f'{name}_preview.tex').write_text(tex)
        shared.render(name,'/tmp/ivg-paper-figures.gX58U6/tectonic')
    (HERE/'engine_source_data.json').write_text(json.dumps(source,indent=2))
    (HERE/'index.html').write_text(webpage())
    with zipfile.ZipFile(HERE/'engine_latex_sources.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(HERE.glob('engine_*.tex')):
            z.write(path,path.name)
        for name in ['engine_source_data.json','build_engine_tables.py','build_review.py','collect_engine_metrics.py']:
            z.write(HERE/name,name)


if __name__=='__main__':
    main()
