# Review round 1 · paper_tex/main.tex · 4 November 2026

The first revision round on the current manuscript, `paper_tex/main.tex` (SHA-256 `be81c734…`, the version after the merge of 4 November). It answers your remark on the Introduction (vague or improper wording, length and repetition, a weak literature review on ground-effect identification) and the GPT review `PAPER_REVIEW_V2.md`.

The round built on the older copy in `SER_Report\...\IEEE_draft___RT_of_mavs\dashboard\round1\` is superseded and should not be used.

## How to start

Double-click `start_dashboard.bat` in this folder. On another system, run `python serve_dashboard.py`. The page opens at http://127.0.0.1:8765. Decisions are saved as you make them. When you are done, press *Save instructions* and tell me "instructions saved".

Do not edit `main.tex` while the round is open: the cards are tied to this version of the file.

## What is on the page

There are 95 cards in manuscript order (32 graded A, 53 B, 10 C):

- 80 cards with text edits (177 edits), shown as current against proposed text;
- 5 rename cards ("near-wall", "Richardson et al.", "Cheeseman-Bennett", the EI margin ξ, and the subscript "safe");
- 10 suggestion cards, which are decisions or new work.

The notes at the top of the page say where to start.

**Sources of the remarks quoted on the cards:**

- your remark on the Introduction;
- the GPT review V2, its 15 major findings;
- a simulated five-seat panel (journal fit, methodology, domain, perspective, devil's advocate);
- a check of Sections II and III against the code and `EXP/CLEAN`;
- a literature search on ground-effect modelling and identification, with every DOI verified;
- a writing audit.

The full texts are in `../../review/`.

**Decisions only you can take** (suggestion cards):

- target journal and length;
- the framing of the paper: the full RT loop, or a two-stage experimental variant;
- the campaign order;
- whether Σ_θ is a covariance or a curvature indicator;
- which model designed the flown π_MB;
- which reward Sec. III-E uses.

## Files

| File | What it is |
|---|---|
| `review_round1.html` | the page; open it through the launcher |
| `main_round1_proposal.pdf` | the paper with every card applied: 18 pages, no errors, no overfull boxes |
| `main_round1_proposal_diff.pdf` | the changes marked (latexdiff) |
| `main_round1_proposal.tex` | the source of the proposal |
| `cards.py`, `review_round1.json`, `round.json` | the cards and their built form |
| `start_dashboard.bat`, `serve_dashboard.py`, `page_template.html`, `cardkit.py` | the dashboard |
| `build_round.py`, `apply_instructions.py`, `test_dashboard.py` | Claude's tools; not for you to run |

The proposal compiles with `references.bib` plus the 35 new entries carried by the cards. Those entries are appended to `references.bib` only when a card that cites them is applied.

## How it was checked

- **Compiled with every card applied:**
  - 18 pages, against 20 today;
  - no LaTeX errors, no undefined references, no overfull boxes;
  - abstract 191 words (208 today); Introduction 2,071 words (1,732 today, the ground-effect literature added);
  - the rest of the text about 1,650 words shorter;
  - 62 references cited (24 today); no existing citation lost.
- **Independent check.** A separate agent, which had not seen the work, read every new text in its paragraph and checked the numbers against the code and data (`review/round1_independent_check.md`). Its seven must-fix findings and its should-fix findings were corrected before delivery.
- **Browser test:** ALL PASS. The page loads and saves, and the saved instructions, applied again, reproduce the proposal exactly.
