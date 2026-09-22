# Revision 4 — wide panels and contextual dialogue

- `environments`: 396 × 145 pt, a three-panel standalone environment figure.
- `interaction_episodes`: 396 × 188 pt, horizontal episode strips with labels in
  the left column. This is the main compact version.
- `interaction_fuller`: 396 × 218 pt, an alternative with fuller user replies.

Main dialogue is 7.25 pt at 396 pt width. Environment descriptions and principal
action captions are 7 pt. Maps, scene details, and native phone UI are contextual;
the vector captions identify the interactions without relying on small UI text.

Dialogue is authored, informed by recorded episode style and current persona
statements. It is not verbatim conversation or a measured model-performance
result. The hard-map fish-and-chips task and screenshots are retained from the
previous engine-verified example. Recovery frames show the food discarded and
the empty plate retained, not successful task completion.

The review page contains a placement check with the unchanged overview. At a
1:2 side-by-side split within 396 pt, dialogue type becomes approximately 4.7 pt;
that arrangement would need its own reduced-content redesign. The standalone
exports and PDF proofs preserve their stated sizes.

Native `.drawio` files contain editable text, shapes, icons, and images. Open them
in diagrams.net, or use the review page's GitHub-backed editing links. Saving to
GitHub requires a connection to your account. This is versioned editing, not
simultaneous live co-editing. Manual edits do not update PDF/SVG exports or the
frozen geometry package automatically.

`source/render.py` replays the reviewed geometry into `source/rendered/` only. It
never overwrites drawings that may have been edited by an author. The included
`workspace_design.py` records layout/text decisions but depends on the original
workspace; use the frozen JSON and renderer for portable reproduction.

Previous figure revisions, the overview, and manuscript figures are unchanged.
