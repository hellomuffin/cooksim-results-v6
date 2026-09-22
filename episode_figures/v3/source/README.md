# Reviewed vector geometry

For everyday editing, open the adjacent native `.drawio` files in diagrams.net.
This optional package reproduces the reviewed geometry programmatically. It is
not a live synchronization bridge: manual drawing edits do not update these JSON
specifications. Re-rendered files go into `rendered/`, never over the shared
drawings or publication exports.

## Reproduce

`render.py` is the portable entry point. `design.py` and `sample_engine.py`
preserve the workspace-specific authoring recipes; they require the simulator
workspace and helper modules, and are not standalone entry points.

Clone the gallery repository so `episode_figures/v3/frames/` and the existing
`figure1/style_reference/fonts/` directory are available. Install Python 3,
Pillow, Inkscape, and fontconfig. Install the supplied IBM Plex font faces for
Inkscape (the browser editor loads the same faces through their public URLs).

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
