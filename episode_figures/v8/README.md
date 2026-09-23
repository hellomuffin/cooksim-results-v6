# Figures · revision 8

- `environments`: larger task descriptions and individual action labels attached to each image. Observations and actions are unchanged from revision 7.
- `overview_dialogue`: existing overview and conversation placed side by side at equal height, with proportional scaling. The overview uses the conversation's font and role palette. No structural reflow or wording changes.
- `overview_matched`: the restyled overview separately.

Open the native `.drawio` sources in diagrams.net. The combined figure contains
two top-level groups and native editable objects within each. Earlier shared
drawings are untouched. Editor saves do not automatically regenerate PDF/SVG.

The combined PDF is a wide native canvas (approximately 956 × 213 pt), retaining
the conversation's text size. Scaling to 396 pt reduces all text proportionally.
The review page includes a paper-width check; no manuscript assets were replaced.

`provenance.json` identifies original native sources, hashes, proportional
transforms, and environment frame crops. `source/` reproduces the environment
geometry. `workspace_composition.py` records the native composition workflow
and depends on the source workspace; it is not a portable replay command.

Observation pixels are preserved. Dialogue is authored, not measured output;
timeline distance is schematic. Recovery snapshots do not show task completion.
