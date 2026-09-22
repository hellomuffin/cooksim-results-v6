# Revision 3 — sampled environments and episode excerpts

- `environments`: wide task rows, separate top-down context, navigation frames,
  omitted-step ellipses, and complete phone screens with gesture overlays.
- `interaction_episodes`: three assistant episode panels. Only B contains two
  user continuations. No early/late taxonomy, recipe panel, or pre-error speech.

The example is **fish and chips in the hard kitchen**, requiring preparation of
two potato portions and frying fish. It replaces the visually weak cheeseburger.
Lettuce is mistakenly plated instead of fried potato. All depicted actions were
executed through the current engine. The prevention branch serves successfully;
the uncorrected branch is rejected. Recovery excerpts stop after emptying the
plate and fetching fresh fish; they do not claim completed recovery.

Dialogue is authored and shortened, guided by the linked real episode transcripts
and current persona statements. It is not a quotation or model-performance result.
Native image pixels are unchanged. Phone hand/ring/trail overlays are annotations.

Open `.drawio` in diagrams.net for native text/shape/image editing. GitHub-backed
saves require your GitHub connection; this is versioned editing, not simultaneous
live co-editing. Manual edits do not regenerate PDFs/SVGs or frozen JSON geometry.
The optional `source/render.py` reproduces the reviewed geometry into `rendered/`
only. It never overwrites a shared drawing.

`paper_proofs.pdf` shows both figures at 396 pt manuscript width. Main episode
dialogue is 8 pt; action captions are 7 pt. Smaller type is secondary annotation.
Original manuscript figures and all prior revisions remain untouched.
