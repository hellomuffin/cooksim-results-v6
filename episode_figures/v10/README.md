# Stacked actor cards and larger dialogue · revision 10

Shared-edit update: preserved the author's wider panel gap from commit
`3176f87` and added aligned, editable subcaptions: “(a) System overview”
and “(b) Example interaction trajectories”. Every existing figure cell is
unchanged. The combined SVG, PDF, and PNG have been regenerated; the shared
editing URL remains the same. The updated PDF is approximately 693 × 230 pt.

Based on the author's second saved native drawing, commit `42331b2`.
All wording and intentional deletions are retained. Shortened dialogue is
rewrapped, Assistant A's shorter episode frame is fitted to its contents,
and a stray timestamp self-loop connector is removed.

The human and assistant are horizontal cards: text left, original icons right.
The assistant is below the human. Only the human has an action interface to
the world; the assistant exchanges messages and user-view observations with
the human. The world task and navigation action fit on single lines.

Conversation takes 58.4% of panel width, excluding the gap. Overall panel
heights match. Arrow labels and dialogue body both use 62 native units
(6.82 pt in the native PDF). At a fixed combined width, dialogue is about
25% larger than revision 9. The native PDF is approximately 683 × 213 pt;
scaling to manuscript width reduces all text proportionally.

Use `overview_dialogue.drawio` for shared editing; the standalone overview is
`overview_matched.drawio`. Prior drawings and manuscript figures are untouched.
The environment figure remains in `../v8/`. Editor saves do not automatically
regenerate exports. Workspace scripts are included for reference, not as a
standalone installation package. Observations retain original pixels.
