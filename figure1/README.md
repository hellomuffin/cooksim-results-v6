# Figure 1 — system overview candidates

Designed at the final **5.5-inch / 396-point manuscript width**. These are proposals for the system-overview figure, not replacements for the cooking teaser currently in the introduction. Figure 2 is unchanged.

## Candidates

| File | Structure | Intended use |
| --- | --- | --- |
| `figure1_a` | Three actors; expanded world with schematic domains and a partial scene graph | Recommended balance of compactness and explanation |
| `figure1_b` | Communication above a wide world-engine panel | When authentic environment views belong in this figure |
| `figure1_c` | Interaction topology separated from environment details | Clearest separation of concepts, but uses more vertical space |
| `figure1_d` | Typographic actor nodes; abstract state-to-progress schematic | Smallest and most restrained; less concrete than A |

## Content decisions

- Only the simulated user acts on the world. The assistant receives user-view video and dialogue and responds through guidance.
- User persona and scheduled events condition the simulated user. No task-input arrow, evaluation box, assistant-to-world control edge, or enclosing user/world frame.
- The action-space contribution appears as **Semantic actions** on the execution interface. API signatures belong in the action table, not in unreadable figure microtext.
- World state supports subgoal checks. The labeled graph in A/B/C illustrates the current VHSim `groceries_hard` task: milk and juice are inside the fridge, but the fridge is still open. The three schematic checks correspond to storing milk, storing juice, and closing the fridge. This is an illustrative state, not a reconstruction of the screenshot or a measured benchmark result. The task and checks were verified in `vh-streaming-engine/tools/episode_goals.py`.
- Environment thumbnails in B/C identify the domains; their UI text is not part of the figure's explanatory content. A/D avoid this small-image issue entirely.
- Schematic options A/D use domain names (Cooking, Household, Mobile UI), so the overview is intelligible before engine names are introduced. The photographic options B/C identify the concrete implementations as CookSim, VHSim, and ScreenSim.

## Files and editing

`*.svg` are layered, self-contained Inkscape masters with live text. `*.pdf` are vector Inkscape exports with embedded fonts, ready for LaTeX. `*.png` are previews. `*.drawio` are native online editing copies with separate text, shapes, and arrows (not flattened images). Actors and interfaces are grouped so their components can be moved together; individual labels remain editable.

Review: https://hellomuffin.github.io/cooksim-results-v6/figure1/

The review page includes two editing modes: **Edit a copy** opens the public source without requiring an account; **Edit shared file** opens the GitHub-backed document and requires GitHub authorization to save. This is versioned collaboration, not a claim of simultaneous Figma-style co-editing. Online edits do not automatically regenerate the manuscript PDF.

After manual editing, treat the edited SVG or draw.io document as authoritative. Do not rerun the generator over hand edits unless those changes have been incorporated into `build.py`. Inkscape is the publication export tool; the browser editor is provided for convenient collaboration. Exporting from draw.io may require setting the final output width back to 5.5 inches: its editing canvas is deliberately 2× larger.

## Rebuild and quality checks

Requirements: Python 3, Pillow, Inkscape, a Liberation Sans or Arial font, and a LaTeX engine for the proof.

```sh
python build.py
tectonic proof.tex
python check.py  # optional: requires PyMuPDF
```

The generator rejects text below 8 pt. Main labels are 9.5–10 pt. `proof.pdf` shows all four candidates at manuscript width alongside 10-pt text. `quality_checks.json` records PDF dimensions, minimum type sizes, embedded fonts, and native editable-object counts. Text, not color alone, identifies actors and interfaces; arrows and line styles preserve the relationships in grayscale. Source figures use no shadows or decorative gradients.

The old `01_simulation_system_v4.pdf` has a minimum font size of approximately 3.3 pt when scaled to this width. The new figures have a minimum of 8 pt. This is a final-size comparison, not the SVG's unscaled coordinate size.

## Screenshot provenance

Images are authentic, unretouched simulator captures, cropped within the SVG to exclude gallery labels and unrelated panels.

- **CookSim:** `cooksim-results-v6/films_r6/classic_expert__gpt-6-astra__b3_medium_nops_hard_map_3.mp4`, 10 seconds; first-person panel. [Gallery repository](https://github.com/hellomuffin/cooksim-results-v6).
- **VHSim:** `vh-streaming-engine/tmp/bench_v3/silent/silent__cx_aftermeal_missing_obj__classic_expert.mp4`, 25 seconds; first-person panel. Captured 2026-09-22 from the current local simulator results.
- **ScreenSim:** `screensim/site_gh/clean/lock_screen_lockdown.png`; the fourth phone view. [Source image](https://hellomuffin.github.io/screensim-gallery/clean/lock_screen_lockdown.png).

## Design references

These informed the structure and production checks; no artwork or wording was copied.

- [Collaborative Gym, Figure 2](https://arxiv.org/html/2412.15701v6): emphasize actors and their interfaces; simplify the details much more aggressively for this overview.
- [τ-voice, Figure 2](https://arxiv.org/abs/2603.13686): distinguish the assistant/user communication channel from the environment interface.
- [PARTNR](https://arxiv.org/abs/2411.00081): separate the top-level interaction story from environment detail, explored in candidate C.
- [Training Proactive and Personalized LLM Agents](https://arxiv.org/abs/2511.02208): attach persona conditioning to the user component rather than spreading it across the diagram.
- [Nature figure preparation guide](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/): editable vector text, consistent typography, final-size checking, restrained styling. The 8-pt minimum here is our ICLR readability choice, not a claim that Nature mandates that size.
- [Ten Simple Rules for Better Figures](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833): prioritize the message, adapt to the output medium, and avoid redundant detail.
- [diagrams.net link documentation](https://www.drawio.com/docs/reference/supported-location-hash-properties/): public-source and GitHub-backed editable links.
