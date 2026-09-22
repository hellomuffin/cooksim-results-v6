# Editable figure candidates

These are review candidates, not replacements for the manuscript figure files.

- `environments_callouts`: preferred environment showcase, with target callouts.
- `environments_minimal`: same examples with quieter annotation.
- `interaction_nested`: preferred hierarchical conversation/action figure.
- `interaction_compact`: shorter branching alternative with an explicit late-only transition.

Each has PDF, SVG, PNG, and native `.drawio` versions. PDF/SVG are 396 pt wide.
The `.drawio` files contain editable text, shapes, connectors, and individual
embedded observations. GitHub-backed diagrams.net saves are versioned, not
simultaneous real-time collaboration. Editing a drawing does not regenerate the
publication exports automatically.

Dialogue is authored to illustrate simulator-executed trajectories. It is not
measured output from named models. `provenance.json` records source-frame hashes,
engine revisions, task checks, action outcomes, and exact crop viewports.
The original observations are retained in `../v1/frames/`; the manifest resolves
their exact paths and hashes. No evidence pixels were
retouched or replaced by generated imagery.

This revision is not regenerated in place once shared: manual source edits are
preserved. Later generated revisions use a different directory.

The nested teaser is 324 pt high; the compact alternative is 269 pt high. Both
retain 8-pt main dialogue and four RGB checkpoints. The environment figure is
245.5 pt high. The placement PDFs show both options in an isolated manuscript
copy, without changing the actual manuscript. Surrounding prose may be outdated.

Design references are BEHAVIOR-1K and ALFRED for the environment showcase, and
Collaborative Gym and Inner Monologue for conversational visual grammar. The
branch hierarchy is original to this figure. The [reference board](../../figure_references/)
links to the corresponding papers. General checks follow the message-first,
medium-aware approach in [Ten Simple Rules for Better Figures](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833).

The optional `source/` package contains replayable vector geometry. It generates
into its own `rendered/` directory and does not overwrite these shared drawings.
