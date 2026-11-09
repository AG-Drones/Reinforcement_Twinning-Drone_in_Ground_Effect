# Review decisions log: paper_tex/main.tex

This is the running record of each round: what was proposed, what was decided (your notes word for word), and what was applied.

## Round 1 (built 4 November 2026)

- **Manuscript:** `paper_tex/main.tex`, SHA-256 `be81c7343b86dbbf2fd766d5f33dae39ea44e7b330120ba891997a28bcd744e3` (CRLF on disk; `a7fcb18e…` with LF line endings).
- **Request:** "ok based on the last version and based on the last review from GPT, which is PAPER_REVIEW_V2, I would like you to use the usual set of skills /deep-academic-research /academic-paper-reviewer /academic-paper /literature-review /scientific-writing /manuscript-review-dashboard to create a dashboard for round of revision 1 for this paper. My general comment, as having read only the intro so far, is that the text is quite ok but sometimes vague and uses improper wording, sometimes is a bit long/repetitive and has a relatively weak literature review on the problem of ground effect identification"
- **Baseline compile:**
  - 20 pages and 0 errors;
  - two overfull boxes (52.4 pt at the covariance equation, 20.3 pt at the reward equation);
  - abstract 208 words; 24 cited keys;
  - Mehra1974, Goodwin1977, Ljung1999, Hjalmarsson2005 and Chiuso2019 are uncited;
  - `references.bib` ends with a stray prose paragraph.
- **Material** (in `review/`):
  - `PAPER_REVIEW_V2.md`, which is in `paper_tex/`;
  - `round1_panel/`, holding the five panel reports;
  - `code_check_current.md`;
  - `literature_ge_identification.md` and `literature_scan_round_SER.md`;
  - `writing_audit.md`;
  - `round1_independent_check.md`;
  - `round1_not_in_cards.md`.
- **Panel outcome:** all five seats recommend major revision. The journal-fit seat suggests IEEE T-CST, which allows at most 16 pages. The panel is simulated: one model family, not calibrated.
- **Cards:** 95 in total (A 32, B 53, C 10). Of these, 80 carry text edits (177 edits), 5 are renames (38 places) and 10 are suggestions.
- **Decisions only you can take:**
  - target journal;
  - framing (full RT or a two-stage variant);
  - campaign order;
  - covariance or curvature indicator;
  - which model designed π_MB;
  - which reward Sec. III-E uses.
- **With every card applied:** 18 pages, no errors, no overfull boxes; abstract 191 words; 62 keys cited.
- **Status:** open, waiting for your decisions.
