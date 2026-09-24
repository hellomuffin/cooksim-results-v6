#!/usr/bin/env python3
"""Read existing rollouts/judgments; compute precise table values, never call models.

Efficiency follows the requested persona-weighted episode-level formula, restricted
to in-time successes. The action and conversation columns use the same subset.
"""
from pathlib import Path
import argparse
import collections
import contextlib
import importlib.util
import json
import os
import statistics
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
KEYS = ['truthful', 'sensible', 'helpful', 'listens', 'economy']


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def row(tag, run, persona, success, action, conversation, a, c):
    return dict(tag=tag, run=run, persona=persona, success=success,
                action=action, conversation=conversation, a=a, c=c,
                efficiency=((a*action+c*conversation)/(a+c)
                            if success == 1 and action is not None and conversation is not None else None))


def collect_cook():
    repo = ROOT / 'cook-bench-engine'
    sys.path[:0] = [str(repo), str(repo/'tools')]
    from cooksim.interact.persona_v2 import ROSTER
    personas = {p.name:p for p in ROSTER}
    cache = json.loads((repo/'tmp/formal_results_cache.json').read_text())
    prefix = str(repo/'tmp/formal_v5/frames')+'/'
    rows = []
    for path, entry in cache.items():
        if not path.startswith(prefix):
            continue
        r = entry.get('rec') or {}
        if not (r.get('g2') and r.get('g3')):
            continue
        p = personas[r['persona']]
        rows.append(row(r['tag'], r['run'], r['persona'], r['in_time'], r['TT'], r['CC'], p.q1, p.q3))
    quality = []
    for path in (repo/'tmp/formal_v5/sq_v4/frames').glob('*/*/b3_*.json'):
        tag = path.parent.name
        if '__r' in tag:
            continue
        d = json.loads(path.read_text())
        ag = d.get('aggregate') or {}
        if ag.get('AQ') is not None:
            quality.append(dict(tag=tag, overall=ag['AQ'], **{k:(ag.get('by_category') or {}).get(k) for k in KEYS}))
    return rows, quality, 'Existing formal_results_cache.json (G2 and G3), full-16 sq_v4 files.'


def collect_vh():
    repo = ROOT/'vh-streaming-engine'
    os.chdir(repo)
    sys.path[:0] = [str(repo/'tools'), str(repo)]
    dump = module(repo/'tools/dump_experiments_vh.py', 'vh_dump_for_table')
    import iv_protocol as P
    rows = []
    for run in (1,2,3):
        per = dump.episode_rows(f'tmp/bench_v{run}')
        for tag, rs in per.items():
            for r in rs:
                if not r.get('fired'):
                    continue
                p = P.PERSONA_ALIASES.get(r['persona'], r['persona'])
                _,_,speed,_,interrupt = P.PERSONA_DIALS[p]
                a, c = P.Q_NUM['speed'][speed], P.Q_NUM['interrupt'][interrupt]
                rows.append(row(tag,run,p,r['S'],r['TT'],r['CC'],a,c))
    quality = []
    for path in (repo/'tmp/bench_v1/sq_v4').glob('*/*.json'):
        d = json.loads(path.read_text())
        ag = d.get('aggregate') or {}
        if ag.get('AQ') is None:
            continue
        hits = collections.defaultdict(list)
        for rd in d.get('rounds') or []:
            for it in (rd.get('items') or {}).values():
                if it.get('category') in KEYS and it.get('pass') is not None:
                    hits[it['category']].append(float(bool(it['pass'])))
        quality.append(dict(tag=path.parent.name, overall=ag['AQ'], **{k:mean(hits[k]) for k in KEYS}))
    return rows, quality, ('Current household dump scorer with measured T_ref; G2. Full-16 AQ. '
                          'Efficiency uses the actual speed/interruption questionnaire levels, '
                          'not assist_metrics.py legacy neutral-speed/binary-interruption weights.')


def collect_screen():
    repo = ROOT/'screensim'
    os.chdir(repo)
    sys.path[:0] = [str(repo),str(repo/'tools')]
    dump = module(repo/'tools/dump_experiments.py','screen_dump_for_table')
    bench = module(repo/'tools/bench_scores.py','screen_bench_for_table')
    from screensim.interact.personas import PERSONAS
    rows = []
    for run in (1,2,3):
        per = bench.load(f'tmp/bench_v{run}')
        for tag, entries in per.items():
            for raw in entries.values():
                r = dump.score(raw)
                p = PERSONAS[raw['persona']]
                rows.append(row(tag,run,p.name,r['in_time'],r['TT'],r['CC'],p.q1,p.q3))
    quality = []
    for path in (repo/'tmp/bench_v1/aq_v4').glob('*/*.json'):
        d = json.loads(path.read_text())
        if d.get('AQ') is not None:
            quality.append(dict(tag=d['contestant'],overall=d['AQ'], **{k:(d.get('by_category') or {}).get(k) for k in KEYS}))
    return rows, quality, ('Current ScreenSim dump scorer with strict goal and no-extra-change checks, '
                          'plus refix overrides. Persona weights use q1/q3. Full-16 rubric, run 1.')


def aggregate(rows, quality):
    out = {}
    for tag in sorted({r['tag'] for r in rows}):
        rtag = [r for r in rows if r['tag']==tag]
        runs = []
        for run in (1,2,3):
            rr = [r for r in rtag if r['run']==run]
            if not rr:
                continue
            won = [r for r in rr if r['success']==1]
            runs.append(dict(run=run,n=len(rr),n_success=len(won),
                             success=mean([r['success'] for r in rr]),
                             **{k:mean([r[k] for r in won]) for k in ['action','conversation','efficiency']}))
        qs = [r for r in quality if r['tag']==tag]
        out[tag] = dict(runs=runs, success=mean([r['success'] for r in runs]),
                        success_sd=statistics.pstdev([r['success'] for r in runs]),
                        **{k:mean([r[k] for r in runs]) for k in ['action','conversation','efficiency']},
                        quality_n=len(qs), quality={k:mean([r[k] for r in qs]) for k in ['overall']+KEYS})
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('engine',choices=['cooksim','vhhome','screensim'])
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    dest=Path(args.out).resolve()
    with contextlib.redirect_stdout(sys.stderr):
        rows,quality,note={'cooksim':collect_cook,'vhhome':collect_vh,'screensim':collect_screen}[args.engine]()
    data=dict(engine=args.engine,models=aggregate(rows,quality),source_note=note,
              efficiency_definition='Per successful episode: (q1*Action + q3*Conversation)/(q1+q3). In-time successes only for all three efficiency columns. Per-run means, then mean across runs with successes.',
              sd_definition='Population SD of three run-level success rates; not a confidence interval.',
              streaming_labels='User confirmed native settings for VHHome and ScreenSim; unsuffixed API records retained. CookSim uses explicitly __native records only.')
    dest.write_text(json.dumps(data,indent=2))
    print(json.dumps(dict(engine=args.engine,episodes=len(rows),quality_episodes=len(quality),output=str(dest))))
