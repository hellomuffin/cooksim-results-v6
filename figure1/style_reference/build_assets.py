"""Download attributed reference figures and self-hosted font specimens.

This builds a design-review board, not a replacement manuscript figure.
"""
from pathlib import Path
import urllib.request
import re
import shutil

ROOT=Path(__file__).resolve().parent
(ROOT/'images').mkdir(exist_ok=True)
(ROOT/'fonts').mkdir(exist_ok=True)
sources={
 'tauvoice':'/tmp/ref-tauvoice.png',
 'latte':'https://latte-web.github.io/static/images/framework.png',
 'sensible':'https://arxiv.org/html/2509.09255v1/prototype_flow_ver2.png',
 'satori':'https://arxiv.org/html/2410.16668v1/user-model4.png',
 'cogym':'https://arxiv.org/html/2412.15701v3/overview.png',
}
for name,url in sources.items():
    target=ROOT/'images'/f'{name}.png'
    if target.exists():continue
    if url.startswith('/'):shutil.copy2(url,target)
    else:urllib.request.urlretrieve(url,target)

query='family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;1,400&family=IBM+Plex+Mono:wght@400&family=Source+Sans+3:wght@400;600&family=Source+Serif+4:ital,wght@1,400&family=Source+Code+Pro:wght@400&family=Manrope:wght@400;600&family=Lora:ital,wght@1,400&family=JetBrains+Mono:wght@400&display=swap'
css=urllib.request.urlopen('https://fonts.googleapis.com/css2?'+query).read().decode()
for i,url in enumerate(dict.fromkeys(re.findall(r'url\((https:[^)]+)\)',css))):
    name=f'face-{i}.ttf'
    target=ROOT/'fonts'/name
    if not target.exists():urllib.request.urlretrieve(url,target)
    css=css.replace(url,'fonts/'+name)
(ROOT/'fonts.css').write_text(css)
for family in ('ibmplexsans','ibmplexserif','ibmplexmono','sourcesans3','sourceserif4','sourcecodepro','manrope','lora','jetbrainsmono'):
    target=ROOT/'fonts'/f'{family}-OFL.txt'
    if not target.exists():urllib.request.urlretrieve(f'https://raw.githubusercontent.com/google/fonts/main/ofl/{family}/OFL.txt',target)
print('Reference images and licensed fonts downloaded.')
