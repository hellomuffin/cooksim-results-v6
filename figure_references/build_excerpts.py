"""Render attributed figure excerpts for design review (not manuscript assets).

Usage: python build_excerpts.py /path/to/downloaded/pdfs
Requires PyMuPDF. Input filenames correspond to the keys below.
"""
import sys
from pathlib import Path
import pymupdf

FIGURES = {
    'behavior': (3, (106, 72, 507, 207)),
    'alfred': (0, (307, 209, 547, 409)),
    'vima': (1, (54, 65, 542, 319)),
    'robocasa365': (0, (107, 454, 505, 672)),
    'teach': (5, (52, 50, 560, 233)),
    'dialfred': (0, (299, 174, 554, 353)),
    'cogym': (1, (106, 76, 506, 270)),
    'inner': (1, (106, 65, 506, 247)),
}
out = Path(__file__).parent / 'images'
out.mkdir(exist_ok=True)
for key, (page, rect) in FIGURES.items():
    with pymupdf.open(Path(sys.argv[1]) / f'{key}.pdf') as doc:
        doc[page].get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=pymupdf.Rect(rect)).save(out / f'{key}.png')
