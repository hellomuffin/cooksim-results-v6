# Environment figure · revision 7

Open `environments.drawio` in diagrams.net for native editing. Text, images,
crop viewports, and shapes remain editable. The review page provides a
GitHub-backed editing link; saving requires your GitHub connection. Manual
edits do not automatically regenerate the PDF/SVG exports.

The environment figure uses colored task strips, enlarged top-down maps,
four consecutive actions followed by an omitted interval and a final action,
and exact upper/lower half-screen phone crops. Action labels are checked
against current engine parsers. The phone trajectory was executed anew and
its full task goal verified. The household observations reuse an executed
reference with labels normalized to the current canonical action vocabulary;
the dispatch test is not a new rollout through the visibility-gated controller.

`provenance.json` records source frames, hashes, crops, and selected actions.
`checks.json` records parser, vector, editor, and export checks.
`source/` reproduces the frozen vector geometry; `fonts/` includes Manrope
and its license. The editor loads the same font files from stable public v5 URLs.

The dialogue figure and its shared editable file remain unchanged in `../v6/`.
Existing shared figures and manuscript assets have not been overwritten.
