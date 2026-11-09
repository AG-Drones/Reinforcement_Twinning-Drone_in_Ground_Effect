# Notes: IEEE draft on experimental Reinforcement Twinning (paper_tex)

## Manuscript and build

- **Manuscript:** `paper_tex/main.tex`, with `references.bib` and the figures in `Methodology/`, `Results/` and `Setups/`.
- **Class and style:** IEEEtran (journal), style IEEEtran.bst.
- **Build:** pdflatex, bibtex, then pdflatex twice. IEEEtran is not installed in the shell on your computer, so Claude compiles in the cloud.
- **Format:** CRLF line endings on disk, American English.
- **Authors:** Alessandro Grava and Miguel A. Mendez.
- **Affiliations:** SAAS (ULB) first and VKI second; UC3M is added for Mendez. No e-mail addresses.
- **Target journal:** not chosen yet. The round-1 panel suggests IEEE T-CST, which allows at most 16 pages.

## Current state (4 November 2026, before round 1 is applied)

| | |
|---|---|
| SHA-256 | be81c7343b86dbbf2fd766d5f33dae39ea44e7b330120ba891997a28bcd744e3 |
| Pages | 20 |
| Errors | 0 |
| Overfull boxes | 2 (l. 651, l. 717) |
| Abstract | 208 words |
| Cited keys | 24 |

## Code and data behind the paper (same repository)

- `jDT/`: the differentiable twin.
- `next_mission_design/`: policy design.
- `adjoint_identification.py`: the post-campaign identification replay.
- `run_next_experiment.py`: the flight script.
- `EXP/CLEAN/`: the averaged records and stored rewards. They hold 41 records and 137 retained flights.
- `paper/pp_paper.py`: the figures.
- Cases BL, INF_01–12, MB, INT_01–02, ALPHA_01–07, EI_01–10 and the generalization cases are mapped to run numbers in `EXP/legacy_name_map.json`.

## Standing preferences (from the review method)

- Sharp and short; each fact once; no defensive or signposting sentences; no colon constructions; sentences under about forty words.
- Every symbol defined where it first appears; every number with its symbol.
- You rewrite your abstract yourself; cards only offer cuts.
- The dashboard, not long lists; short final messages.
