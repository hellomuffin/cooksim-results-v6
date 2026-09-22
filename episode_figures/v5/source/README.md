# Reviewed vector geometry

For everyday editing, open the adjacent native `.drawio` files in diagrams.net.
This optional package reproduces the reviewed geometry programmatically. It is
not a live synchronization bridge: manual drawing edits do not update these JSON
specifications. Re-rendered files go into `rendered/`, never over the shared
drawings or publication exports.

## Reproduce

Clone the gallery repository, preserving the adjacent `../frames/` and
`../fonts/` directories. Install Python 3, Pillow, Inkscape, and fontconfig.
Install the supplied Manrope regular and semibold fonts and refresh the font
cache. The browser editor loads these same font faces through their public URLs.

Run, for example:

```sh
python render.py environments.json interaction_episodes.json
```

Text, shapes, line geometry, grouping, image source paths, and crop viewports are
explicit in each JSON specification. Pixels are not edited: SVG viewports crop
the original engine screenshots. The output is PDF, SVG, PNG, and native draw.io.
The exact original observations and their hashes are recorded in the provenance
manifest. Persona axes in the teaser are illustrative dispositions, not measured
persona-conditioned success rates.

`workspace_design.py` records the high-level design recipe but depends on the
original workspace manifests. `render.py` is the portable entry point. Fonts
are licensed under the adjacent SIL Open Font License.
